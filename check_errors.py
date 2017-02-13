#!/usr/bin/python
import argparse
import nagiosplugin
from elasticsearch import Elasticsearch

class Errors(nagiosplugin.Resource):
    def __init__(self, elasticsearchServer, env, profile, begin, finish):
        self.elasticsearchServer = elasticsearchServer
        self.begin = begin
        self.finish = finish
        self.env = env
        self.profile = profile

    def probe(self):
        client = Elasticsearch([self.elasticsearchServer])

        response = client.count(
            index="nginx-*",
            body={
                "query" : {
                    "bool": {
                        "must": [
                            { "term": {"env": self.env}},
                            { "term": {"profile": self.profile}},
                            { "range": {
                                "response": {
                                    "gte": self.begin,
                                    "lte": self.finish }}},
                            { "range": {
                                "timestamp": {
                                    "gte": "now-1h"
                                }
                            }
                            }
                        ],
                    }
                }
            })

        return [nagiosplugin.Metric('The number of errors', response['count'], min=0, context='response')]

@nagiosplugin.guarded
def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('-w', '--warning', type=int, default=0,
                      help='return warning if the number of erros is outside RANGE')
    argp.add_argument('-c', '--critical', type=int, default=0,
                      help='return critical if the number of erros is outside RANGE')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity')
    argp.add_argument('-H', '--host', action='store', default='',
                      help='increase')
    argp.add_argument('-e', '--env', action='store', default='',
                      help='count response code for environment')
    argp.add_argument('-p', '--profile', action='store', default='',
                      help='count response code for profile')
    argp.add_argument('-b', '--begin', action='store', default='',
                      help='count response code from VALUE')
    argp.add_argument('-f', '--finish', action='store', default='',
                      help='count response code until VALUE')
    args = argp.parse_args()

    check = nagiosplugin.Check(
        Errors(elasticsearchServer=args.host, env=args.env, profile=args.profile, begin=args.begin, finish=args.finish),
        nagiosplugin.ScalarContext('response', nagiosplugin.Range("%d" % args.warning), nagiosplugin.Range("%d" % args.critical)))
    check.main(verbose=args.verbose)

if __name__ == '__main__':
    main()