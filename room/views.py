from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Room, Message, Invitation
from .forms import RoomCreateForm, InviteUserForm # type: ignore
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.db.models import Q

@login_required
def kick_user(request, room_slug, user_id):
    room = get_object_or_404(Room, slug=room_slug)
    if request.user != room.owner:
        return HttpResponseForbidden("Apenas o dono consegue expulsar!")

    user_to_kick = get_object_or_404(User, id=user_id)
    if user_to_kick == room.owner:
        return HttpResponseForbidden("Impossivel expulsar o dono.")

    room.participants.remove(user_to_kick)
    # Optionally: send notification to kicked user, or redirect somewhere
    return redirect('room_detail', slug=room.slug)  # Changed room_slug to slug

@login_required
def invite_user(request, user_id):
    target = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = InviteUserForm(request.POST, user=request.user)
        if form.is_valid():
            room = form.cleaned_data['room']
            
            # Check if user is already in the room
            if target in room.participants.all():
                messages.warning(request, f"{target.username} já está na sala “{room.name}”.")
            else:
                # Check if there's already a pending invite
                existing_invite = Invitation.objects.filter(
                    room=room,
                    invited_user=target,
                    accepted=None
                ).exists()
                
                if existing_invite:
                    messages.warning(request, f"{target.username} já tem um convite pendente para “{room.name}”.")
                else:
                    # Create new invitation
                    Invitation.objects.create(
                        room=room,
                        invited_user=target,
                        invited_by=request.user
                    )
                    messages.success(request, f"Convite enviado para {target.username} para “{room.name}”!")
                    
                    # Create a system message in the room
                    Message.objects.create(
                        room=room,
                        user=request.user,
                        content=f"{request.user.username} invited {target.username} to join."
                    )

            return redirect('user_info', user_id=user_id)
    else:
        form = InviteUserForm(user=request.user)

    return render(request, 'room/invite_user.html', {
        'form': form,
        'target': target,
    })


@login_required
def accept_invite(request, invitation_id):
    invite = get_object_or_404(
        Invitation,
        id=invitation_id,
        invited_user=request.user
    )

    if invite.accepted is not None:
        return HttpResponseBadRequest("This invitation has already been processed.")

    # Use the model's accept method, which now handles duplicates
    invite.accept()
    messages.success(request, f"You've joined {invite.room.name}!")
    return redirect('room_detail', slug=invite.room.slug)

@login_required
def reject_invite(request, invitation_id):
    invite = get_object_or_404(Invitation, id=invitation_id, invited_user=request.user)
    
    if invite.accepted is not None:
        return HttpResponseBadRequest("This invitation has already been processed.")
    
    invite.reject()
    messages.info(request, f"You've declined the invitation to {invite.room.name}.")
    return redirect('rooms')  # Or wherever you want to redirect after rejection

# room/views.py

@login_required
def convite_pendente(request):
    # mark all not-yet-viewed pending invites as viewed
    Invitation.objects.filter(
        invited_user=request.user,
        accepted=None,
        viewed=False
    ).update(viewed=True)

    # fetch *all* pending to display them
    pending = Invitation.objects.filter(
        invited_user=request.user,
        accepted=None
    ).select_related('room','invited_by')

    return render(request, 'room/convite_pendente.html', {
        'convite_pendente': pending
    })


@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomCreateForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = request.user
            room.save()
            room.participants.add(request.user)
            return redirect('rooms')
    else:
        form = RoomCreateForm()
    return render(request, 'room/create_room.html', {'form': form})

@login_required
def room_detail(request, slug):
    room = get_object_or_404(Room, slug=slug)
    # deny access if private and user not in participants
    if room.is_private and request.user not in room.participants.all():
        return render(request, 'room/forbidden.html', status=403)

    messages = room.messages.all()[:25]
    users = room.participants.all()
    return render(request, 'room/room.html', {
        'room': room,
        'messages': messages,
        'users': users
    })

@login_required
def rooms(request):
    rooms = Room.objects.filter(
        Q(owner=request.user) | 
        Q(participants=request.user)
    ).distinct()
    return render(request, 'room/rooms.html', {'rooms': rooms})

@login_required
def rooms(request):
    rooms = Room.objects.filter(
        Q(owner=request.user) | Q(participants=request.user)
    ).distinct()

    # count pending unviewed invites for badge
    pending_count = Invitation.objects.filter(
        invited_user=request.user,
        accepted=None,
        viewed=False
    ).count()

    return render(request, 'room/rooms.html', {
        'rooms': rooms,
        'pending_invite_count': pending_count,
    })

@login_required
def chatroom(request):
    if request.method == "POST":
        message_text = request.POST.get("message")
        if message_text:
            Message.objects.create(user=request.user, text=message_text)
        return redirect("room")

    messages = Message.objects.all()
    return render(request, "room/room.html", {"messages": messages})
