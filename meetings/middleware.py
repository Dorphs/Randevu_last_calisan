import time
import logging
from django.db import connection
from django.conf import settings
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

# Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

class MonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # Request processing
        response = self.get_response(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log request details
        logger.info(
            'Request processed',
            extra={
                'path': request.path,
                'method': request.method,
                'status_code': response.status_code,
                'duration': duration,
                'user': str(request.user),
            }
        )
        
        # Update Prometheus metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.path
        ).observe(duration)
        
        # Log slow requests
        if duration > settings.SLOW_REQUEST_THRESHOLD:
            logger.warning(
                'Slow request detected',
                extra={
                    'path': request.path,
                    'method': request.method,
                    'duration': duration,
                }
            )
        
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Log view function calls
        logger.info(
            'View function called',
            extra={
                'view': view_func.__name__,
                'args': view_args,
                'kwargs': view_kwargs,
            }
        )
        return None

class QueryLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Clear queries log
        connection.queries_log.clear()
        
        # Process request
        response = self.get_response(request)
        
        # Log database queries
        for query in connection.queries:
            duration = float(query['time'])
            
            # Update Prometheus metrics
            db_query_duration_seconds.labels(
                query_type=query['sql'][:50]
            ).observe(duration)
            
            # Log slow queries
            if duration > settings.SLOW_QUERY_THRESHOLD:
                logger.warning(
                    'Slow query detected',
                    extra={
                        'sql': query['sql'],
                        'duration': duration,
                    }
                )
        
        return response
