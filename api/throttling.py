from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle

class BurstRateThrottle(UserRateThrottle):
    """
    Throttle for burst requests (high rate for short periods)
    """
    scope = 'burst'
    rate = '60/minute'

class SustainedRateThrottle(UserRateThrottle):
    """
    Throttle for sustained requests (lower rate for longer periods)
    """
    scope = 'sustained'
    rate = '1000/day'

class HighVolumeEndpointThrottle(UserRateThrottle):
    """
    Throttle for high-volume endpoints like search
    """
    scope = 'high_volume'
    rate = '30/minute'

class AnonymousThrottle(AnonRateThrottle):
    """
    Stricter throttle for anonymous users
    """
    scope = 'anonymous'
    rate = '20/minute'

class MarketplaceThrottle(ScopedRateThrottle):
    """
    Specific throttle for marketplace endpoints
    """
    scope = 'marketplace'
    rate = '100/hour'

class RecommendationsThrottle(ScopedRateThrottle):
    """
    Specific throttle for recommendations endpoints
    """
    scope = 'recommendations'
    rate = '50/hour'

class AuthThrottle(ScopedRateThrottle):
    """
    Specific throttle for authentication endpoints
    """
    scope = 'auth'
    rate = '10/minute'