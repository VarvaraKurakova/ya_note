from django.urls import reverse

SLUG = 'Zametka-1'

LOGIN_URL = reverse('users:login')
NOTES_DETAIL_URL = reverse('notes:detail', args=(SLUG,))
NOTES_EDIT_URL = reverse('notes:edit', args=(SLUG,))
NOTES_DELETE_URL = reverse('notes:delete', args=(SLUG,))
HOMEPAGE_URL = reverse('notes:home')
SIGNUP_URL = reverse('users:signup')
LOGOUT_URL = reverse('users:logout')
NOTE_LIST_URL = reverse('notes:list')
NOTES_ADD_URL = reverse('notes:add')
NOTE_CREATE_SUCCESS_URL = reverse('notes:success')
