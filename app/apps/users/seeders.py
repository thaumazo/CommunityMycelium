from django.contrib.auth import get_user_model

User = get_user_model()

def seed_users():
    # Create first user
    User.objects.create_user(
        username='whitnelson',
        email='whitnelson@gmail.com',
        password='Asdfdsa1..'
    )
    
    # Create second user
    User.objects.create_user(
        username='willgarrison',
        email='willgarrison@gmail.com',
        password='Asdfdsa1..'
    ) 