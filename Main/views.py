import asyncio
import json
from multiprocessing import Process

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .helpers import get_users_fields, all_users_fields, read_data, chain_interpreter
from .models import Token, Config


@login_required
def index(request):
    if request.method == 'POST':
        chain = request.POST['chain']
        ids = read_data(request.POST['ids'])
        dumped_ids = json.dumps(ids)
        photo_type = request.POST['photo_type']
        fields = get_users_fields(request)
        limit_groups = request.POST['limit_groups']
        limit_members = request.POST['limit_members']
        limit_photos = request.POST['limit_photos']
        limit_posts = request.POST['hard_limit_posts']
        hard_limit_groups = request.POST['hard_limit_groups']
        hard_limit_members = request.POST['hard_limit_members']
        hard_limit_photos = request.POST['hard_limit_photos']
        hard_limit_posts = request.POST['hard_limit_posts']
        config = Config.objects.create(chain=chain, ids=dumped_ids, photo_type=photo_type, fields=fields,
                                       limit_groups=limit_groups, limit_members=limit_members,
                                       limit_photos=limit_photos, limit_posts=limit_posts,
                                       hard_limit_groups=hard_limit_groups,
                                       hard_limit_members=hard_limit_members, hard_limit_photos=hard_limit_photos,
                                       hard_limit_posts=hard_limit_posts, interpreted_chain=chain_interpreter(chain),
                                       remaining_chain=chain, progress=0, original_chain=chain)
        tokens = [token.get('token') for token in list(Token.objects.values())]
        t = Process(target=asyncio.run, args=(config.start_executing(tokens),), kwargs={})
        t.start()
        return redirect('active_process')
    elif request.method == 'GET':
        processes = Config.objects.all()
        if processes.count() == 0:
            context = {
                'fields': all_users_fields()
            }
            return render(request, 'index.html', context)
        else:
            return redirect('active_process')


@login_required
def active_process(request):
    if request.method == 'POST' and 'reload' in request.POST:
        config = Config.objects.last()
        new_progress = (len(config.original_chain) - len(config.remaining_chain)) / len(config.original_chain)
        new_config = Config(chain=config.remaining_chain, ids=config.ids, photo_type=config.photo_type,
                            fields=config.fields, limit_groups=config.limit_groups,
                            limit_members=config.limit_members, limit_photos=config.limit_photos,
                            limit_posts=config.limit_posts, hard_limit_posts=config.hard_limit_posts,
                            interpreted_chain=config.interpreted_chain,
                            remaining_chain=config.remaining_chain,
                            progress=new_progress * 100, original_chain=config.original_chain)
        config.delete()
        new_config.save()
        tokens = [token.get('token') for token in list(Token.objects.values())]
        t = Process(target=asyncio.run, args=(new_config.start_executing(tokens),), kwargs={})
        t.start()
        return render(request, 'active_process.html')
    elif request.method == 'POST' and 'reload_tokens' in request.POST:
        config = Config.objects.last()
        config.need_to_reload_tokens()
        return render(request, 'active_process.html')

    elif request.method == 'POST':
        config = Config.objects.last()
        if config is not None:
            progress = round(config.progress)
            errors = config.errors
            return JsonResponse({"progress": progress, "errors": errors})
        else:
            return JsonResponse({"progress": 'Finished'})

    elif request.method == 'GET':
        return render(request, 'active_process.html')
