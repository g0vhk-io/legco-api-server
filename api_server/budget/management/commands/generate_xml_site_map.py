from django.core.management.base import BaseCommand, CommandError
from budget.models import Reply, Meeting
from lxml import etree
from django.template import loader
from datetime import date

class Command(BaseCommand):
    help = 'Generate XML sitemap'

    def add_arguments(self, parser):
        parser.add_argument('output', type=str)

    def handle(self, *args, **options):
        print(options['output'])
        template = loader.get_template('budget/sitemap.xml')
        root = 'http://budget.g0vhk.io'
        locations = ['/']
        locations += [root + '/reply/' + r.key for r in Reply.objects.all()]
        meetings = [root + '/meeting/%s/%s' % (m.year, m.bureau.bureau) for m in Meeting.objects.all() ]
        locations += meetings
        d = date.today().strftime('%Y-%m-%d')
        print(d)
        pages = [{'loc': l, 'lastmod': d, 'changefreq': 'daily'} for l in locations]
        context = {
            'pages': pages
        }
        with open(options['output'], 'w') as f:
            f.write(template.render(context, None))
