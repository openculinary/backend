from collections import namedtuple
import csv
import psycopg2
import sys


class WDCRecipeImport(object):

    BATCH_COMMIT_SIZE = 100
    TYPE_RECIPE = '<http://schema.org/Recipe>'

    nquad = namedtuple('nquad', ['subject', 'predicate', 'object', 'label'])

    def __init__(self):
        self.valid_predicates = self._read_predicates()
        self.conn = psycopg2.connect('')
        self.cursor = self.conn.cursor()
        self._init_tables()
        self.recipe_count = 0
        self.relation_count = 0

    @staticmethod
    def _read_predicates():
        with open('predicates.txt') as p:
            predicates = p.readlines()
            predicates = [pred.strip() for pred in predicates]
            predicates = set(predicates)
        return predicates

    def _init_tables(self):
        self.cursor.execute('drop table if exists recipes')
        self.cursor.execute('create table recipes' +
                            '(id text, url text)')
        self.cursor.execute('drop table if exists relations')
        self.cursor.execute('create table relations' +
                            '(relation_id text, predicate text, value text)')

    def _parse_nquad(self, line):
        subj, pred, obj, label, _ = line

        if not subj.startswith('_:genid'):
            return

        pred = pred.split('/')[-1].replace('>', '', 1)
        pred = pred.split('#')[-1]
        if pred not in self.valid_predicates:
            return

        label = label[1:-1]

        return self.nquad(
            subject=subj,
            predicate=pred,
            object=obj,
            label=label
        )

    def _handle_recipe(self, nquad):
        self.cursor.execute(
            'insert into recipes (id, url) values (%s, %s)',
            (nquad.subject, nquad.label)
        )
        self.recipe_count += 1
        if self.recipe_count % self.BATCH_COMMIT_SIZE == 0:
            self.conn.commit()

    def _handle_relation(self, nquad):
        if not nquad.object.strip():
            return

        self.cursor.execute(
            'insert into relations (relation_id, predicate, value)' +
            'values (%s, %s, %s)',
            (nquad.subject, nquad.predicate, nquad.object)
        )
        self.relation_count += 1
        if self.relation_count % self.BATCH_COMMIT_SIZE == 0:
            self.conn.commit()

    def parse(self):
        reader = csv.reader(
            sys.stdin,
            delimiter=' ',
            quotechar='"',
            escapechar='\\',
            doublequote=False
        )

        for line in reader:
            nquad = self._parse_nquad(line)
            if not nquad:
                continue

            if nquad.predicate == 'type':
                if nquad.object == self.TYPE_RECIPE:
                    self._handle_recipe(nquad)
            else:
                self._handle_relation(nquad)

        self.conn.commit()
        print(
            'Import complete - recipe_count:{}, relation_count:{}'
            .format(self.recipe_count, self.relation_count)
        )


parser = WDCRecipeImport()
parser.parse()
