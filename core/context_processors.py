from django.conf import settings


def stripe_public_key(request):
    """Expose the Stripe publishable key to all templates as STRIPE_PUBLIC_KEY."""
    return {
        'STRIPE_PUBLIC_KEY': getattr(settings, 'STRIPE_PUBLIC_KEY', '')
    }
