from otree.api import *
import numpy.random as rnd
import random
import pandas as pd

doc = """
Your app description
"""

class C(BaseConstants):
    NAME_IN_URL = 'Task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 54  # 54 trials per participant
    NUM_PROUNDS = 3
    lAttrID = ['p', 's', 'c']
    lAttrNames = ['Price', 'Sustainability', 'Label']
    lColNames = ['Product A', 'Product B']
    BetweenTrialMessages = {
        "1": f"Now you will have {NUM_PROUNDS} practice rounds.",
        str(NUM_PROUNDS + 1): "The practice rounds are over."
    }
    imgLeafs = "global/figures/leafs/leaf_"
    imgLabels = "global/figures/labels/label_"
    imgPrices = "global/figures/prices/n_"
    imgProducts = "global/figures/products/product_"

    iLikertConf = 7
    sConfQuestion = f"From 1 to {iLikertConf}, how confident are you on your choice?"
    sLeftConf = "Very unsure"
    sRightConf = "Very sure"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    sChoice = models.StringField()
    dRT_dec = models.FloatField()
    iConfidence = models.IntegerField()
    dRT_conf = models.FloatField()
    P1 = models.IntegerField()
    P2 = models.IntegerField()
    S1 = models.IntegerField()
    S2 = models.IntegerField()
    Q1 = models.IntegerField()
    Q2 = models.IntegerField()
    sNames = models.LongStringField(blank=True)
    sDT = models.LongStringField(blank=True)
    sStartDec = models.StringField()
    sEndDec = models.StringField()
    sStartCross = models.StringField()
    sEndCross = models.StringField()
    sStartConf = models.StringField()
    sEndConf = models.StringField()
    sBetweenBtn = models.StringField()
    Product1 = models.IntegerField()
    Product2 = models.IntegerField()


# Add this PARTICIPANT_FIELDS definition to include the custom field
PARTICIPANT_FIELDS = ['lPos', 'iSelectedTrial', 'trials', 'sTreatment']


def creating_session(subsession):
    if subsession.round_number == 1:
        players = subsession.get_players()
        for player in players:
            p = player.participant

            # Randomize order of attributes
            lPos = C.lAttrID[:]
            random.shuffle(lPos)
            p.lPos = lPos

            # Select trial for payment
            p.iSelectedTrial = random.randint(C.NUM_PROUNDS + 1, C.NUM_ROUNDS)

            # Generate 54 trials with equal likelihood of price conditions
            trials = generate_trials()

            # Assign the trials to the participant
            p.trials = trials

    for player in subsession.get_players():
        p = player.participant
        player.sBetweenBtn = random.choice(['left', 'right'])

        if player.round_number <= C.NUM_PROUNDS:
            # Practice Trials
            lValues = {
                1: [1, 2, 1, 1, 1, 1],
                2: [1, 1, 1, 2, 1, 1],
                3: [1, 1, 1, 1, 1, 2]
            }.get(player.round_number, [1, 1, 1, 1, 1, 1])
            p.sTreatment = 'Practice'
            player.Product1, player.Product2 = 1, 2  # Practice products
        else:
            # Normal Trials
            trial_index = player.round_number - C.NUM_PROUNDS - 1
            trial = p.trials[trial_index]
            p.sTreatment = trial['condition']
            lValues = trial['values']
            lValues = [int(value) for value in lValues]  # Convert values to integers
            player.Product1, player.Product2 = trial['products']

        player.P1, player.P2, player.S1, player.S2, player.Q1, player.Q2 = lValues


def generate_trials():
    # Initialize the combinations
    combinations = []

    # Define the price sets with image paths
    price_sets = {
        'TruePrice': ["7", "8", "9"],
        'PlainPrice': ["4", "5", "6"],
        'PriceRating': ["1", "2", "3"]
    }
    sustainability_values = ["1", "2", "3"]
    credentials_values = ["1", "2"]  # Government and Commercial
    product_pairs = [(1, 2), (3, 4), (5, 6)]

    # Generate trials for each price condition
    for condition, price_set in price_sets.items():
        for v1 in range(3):
            for v2 in range(3):
                if v1 != v2:
                    # Generate trials where price and sustainability change
                    for s1 in range(3):
                        for s2 in range(3):
                            if s1 != s2:
                                values = [int(price_set[v1]), int(price_set[v2]), int(sustainability_values[s1]), int(sustainability_values[s2]), 1, 1]
                                products = random.choice(product_pairs)
                                combinations.append({'values': values, 'condition': condition, 'products': products})

                    # Generate trials where price and label change
                    for q1 in range(2):
                        for q2 in range(2):
                            if q1 != q2:
                                values = [int(price_set[v1]), int(price_set[v2]), 1, 1, int(credentials_values[q1]), int(credentials_values[q2])]
                                products = random.choice(product_pairs)
                                combinations.append({'values': values, 'condition': condition, 'products': products})

    # Shuffle combinations to ensure random order
    random.shuffle(combinations)

    return combinations[:54]  # Return only the first 54 combinations to meet the required number of trials


def attributeList(lValues, lPos, condition, product_pair):
    lAttributes = []
    lOrder = []

    # Add product pair at the top without the 'Product' name
    lAttributes.append({
        'id': 'Product',
        'name': '',
        'lValues': [f"{C.imgProducts}{product_pair[0]}.png", f"{C.imgProducts}{product_pair[1]}.png"]
    })

    for i in range(len(C.lAttrID)):
        id = C.lAttrID[i]
        name = C.lAttrNames[i]
        lOrder.append(lPos.index(id))
        lPaths = []
        for v in lValues[i]:
            if id == "s":
                lPaths.append(f"{C.imgLeafs}{v}.png")
            elif id == "p":
                lPaths.append(f"{C.imgPrices}{v}.png")  # Use imgPrices for all price conditions
            else:
                lPaths.append(f"{C.imgLabels}{v}.png")

        Attr = {
            'id': id,
            'name': name,
            'lValues': lPaths,
        }
        lAttributes.append(Attr)

    lFinal = [lAttributes[0]] + [lAttributes[x + 1] for x in lOrder]
    return lFinal

class Message(Page):
    template_name = 'global/Message.html'

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_PROUNDS
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            MessageText = 'The practice rounds are over. <br> The experiment will start now.'
        )

class Decision(Page):
    form_model = 'player'
    form_fields = ['sStartDec', 'sEndDec', 'dRT_dec', 'sNames', 'sDT', 'sChoice']

    @staticmethod
    def vars_for_template(player: Player):
        p = player.participant
        lPos = p.lPos
        condition = p.sTreatment
        lValues = [
            [player.P1, player.P2],
            [player.S1, player.S2],
            [player.Q1, player.Q2]
        ]
        product_pair = (player.Product1, player.Product2)
        return dict(
            lAttr=attributeList(lValues, lPos, condition, product_pair),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Log the values to ensure they are being captured correctly
        print('Before next page values:', {
            'sNames': player.sNames,
            'sDT': player.sDT,
            'sChoice': player.sChoice
        })

class FixCross(Page):
    form_model = 'player'
    form_fields = ['sStartCross', 'sEndCross']
    template_name = 'global/FixCross.html'


class SideButton(Page):
    form_model = 'player'
    form_fields = ['sStartCross', 'sEndCross']
    template_name = 'global/SideButton.html'

    @staticmethod
    def js_vars(player: Player):
        return dict(
            sPosition=player.sBetweenBtn
        )


class Confidence(Page):
    form_model = 'player'
    form_fields = ['sStartConf', 'sEndConf', 'dRT_conf', 'iConfidence']
    template_name = 'global/Confidence.html'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            lScale=list(range(1, C.iLikertConf + 1))
        )


page_sequence = [SideButton, Decision, Confidence, Message]

# Ensure that SESSION_CONFIGS includes the app
SESSION_CONFIGS = [
    dict(
        name='task',
        display_name='Task',
        num_demo_participants=1,
        app_sequence=['Task']
    ),
]
