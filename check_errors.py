#!/usr/bin/python
import argparse
import nagiosplugin
from elasticsearch import Elasticsearch

class Errors(nagiosplugin.Resource):
    def __init__(self, elasticsearchServer, begin, finish):
        self.elasticsearchServer = elasticsearchServer
        self.begin = begin
        self.finish = finish

    def probe(self):
        client = Elasticsearch([self.elasticsearchServer])

        response = client.count(
            index="nginx-*",
            body={
                "query" : {
                    "bool": {
                        "must": [
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
    argp.add_argument('-b', '--begin', action='store', default='',
                      help='count response code from VALUE')
    argp.add_argument('-f', '--finish', action='store', default='',
                      help='count response code until VALUE')
    args = argp.parse_args()

    check = nagiosplugin.Check(
        Errors(elasticsearchServer=args.host, begin=args.begin, finish=args.finish),
        nagiosplugin.ScalarContext('response', nagiosplugin.Range("%d" % args.warning), nagiosplugin.Range("%d" % args.critical)))
    check.main(verbose=args.verbose)

if __name__ == '__main__':
    main()