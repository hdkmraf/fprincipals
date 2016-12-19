import unittest

from ..items import ForeignPrincipalItemLoader


__all__ = ('ForeignPrincipalsItemLoadersTestCase',)


class ForeignPrincipalsItemLoadersTestCase(unittest.TestCase):

    def test_item_loader(self):
        input = {
            'address': [u'P.O. Box 547', u'Government Road', u'Manama\xa0\xa0'],
            'country': u'AFGHANISTAN',
            'date': u'05/26/2011',
            'exhibit_url': u'http://www.fara.gov/docs/5839-Exhibit-AB-20110526-21.pdf',
            'foreign_principal': u'Ministry of Foreign Affairs Kingdom of Bahrain',
            'reg_num': u'5839',
            'registrant': u'Sorini, Samet & Associates, LLC',
            'state': None,
            'url': u'https://efile.fara.gov/pls/apex/f?p=171:200:::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:5839,Exhibit%20AB,BAHRAIN'
        }

        item_loader = ForeignPrincipalItemLoader()

        item_loader.add_value(None, input)

        self.assertEqual(
            item_loader.load_item(),
            {
                'address': u'P.O. Box 547\nGovernment Road\nManama\xa0\xa0',
                'country': u'AFGHANISTAN',
                'date': u'2011-05-26T00:00:00',
                'exhibit_url': u'http://www.fara.gov/docs/5839-Exhibit-AB-20110526-21.pdf',
                'foreign_principal': u'Ministry of Foreign Affairs Kingdom of Bahrain',
                'reg_num': u'5839',
                'registrant': u'Sorini, Samet & Associates, LLC',
                'url': u'https://efile.fara.gov/pls/apex/f?p=171:200:::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:5839,Exhibit%20AB,BAHRAIN'
             }
        )
