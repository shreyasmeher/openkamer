import json
import logging
from typing import List

from wikidata import wikidata

logger = logging.getLogger(__name__)


class GovernmentMemberData:
    def __init__(self):
        self.position_name = ''
        self.position = None
        self.properties = []
        self.wikidata_id = None
        self.wikipedia_url = None
        self.name = None
        self.parlement_and_politiek_id = None
        self.ministry = None
        self.start_date = None
        self.end_date = None


def get_government_members(government_wikidata_id, max_members=None) -> List[GovernmentMemberData]:
    logger.info('BEGIN')
    language = 'nl'
    parts = wikidata.WikidataItem(government_wikidata_id).get_parts()
    members = []
    
    # --- Start of the fix ---
    # Add a check to ensure 'parts' is not None before trying to loop over it.
    # This prevents a crash if the Wikidata API returns an empty or unexpected result for a government.
    if parts:
        for part in parts:
            member = create_government_member(part, language)
            logger.info(member.name)
            logger.info(json.dumps(member.__dict__, sort_keys=True, default=str))
            members.append(member)
            if max_members and len(members) >= max_members:
                break
    # --- End of the fix ---

    logger.info('END')
    return members


def create_government_member(part, language) -> GovernmentMemberData:
    member = GovernmentMemberData()
    member.wikidata_id = part['mainsnak']['datavalue']['value']['id']
    member_item = wikidata.WikidataItem(member.wikidata_id)
    member.wikipedia_url = member_item.get_wikipedia_url(language=language)
    member.name = member_item.get_label(language=language)
    member.parlement_and_politiek_id = member_item.get_parlement_and_politiek_id()
    for prop_id in part['qualifiers']:
        prop = part['qualifiers'][prop_id][0]
        # print(json.dumps(prop, sort_keys=True, indent=2))
        if prop['datatype'] == 'wikibase-item':
            item_id = prop['datavalue']['value']['id']
            item = wikidata.WikidataItem(item_id)
            is_without_portfolio = item.is_subclass_of_minister_without_portfolio()
            if is_without_portfolio:
                member.position = 'minister zonder portefeuille'
            item_label = item.get_label(language=language)
            item_label = item_label.lower()
            member.properties.append(item_label)
            if 'ministerie' in item_label:
                member.ministry = item_label.replace('ministerie van', '').strip()
            elif 'nederlands minister voor' in item_label or 'nederlands minister van' in item_label:
                member.position_name = item_label.replace('nederlands minister voor', '').replace('nederlands minister van', '').strip()
            elif 'minister voor' in item_label or 'minister van' in item_label:
                member.position_name = item_label.replace('minister voor', '').replace('minister van', '').strip()
            if member.position is None:
                if 'viceminister' in item_label or 'vicepremier' in item_label:
                    member.position = 'viceminister-president'
                elif 'minister-president' in item_label or 'premier' in item_label:
                    member.position = 'minister-president'
                elif 'staatssecretaris' in item_label:
                    member.position = 'staatssecretaris'
                elif 'minister zonder portefeuille' in item_label:
                    member.position = 'minister zonder portefeuille'
                elif 'minister ' in item_label or 'nederlandse minister' in item_label or 'minister' == item_label:
                    member.position = 'minister'
        if prop['property'] == 'P580':  # start time
            member.start_date = wikidata.WikidataItem.get_date(prop['datavalue']['value']['time'])
        if prop['property'] == 'P582':  # end time
            member.end_date = wikidata.WikidataItem.get_date(prop['datavalue']['value']['time'])
    return member


def get_government(government_wikidata_id):
    item = wikidata.WikidataItem(government_wikidata_id)
    return {
        'name': item.get_label(language='nl'),
        'start_date': item.get_start_time() or item.get_inception(),
        'end_date': item.get_end_time() or item.get_dissolved(),
    }