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
    lAttrNames = ['Price', 'Sustainability', 'Labels']
    lColNames = ['Product A', 'Product B']
    BetweenTrialMessages = {
        "1": f"Now you will have {NUM_PROUNDS} practice rounds.",
        str(NUM_PROUNDS + 1): "The practice rounds are over."
    }
    imgCandidate = "global/figures/candidate.png"
    imgStars = "global/figures/stars/star_"
    imgLeafs = "global/figures/leafs/leaf_"
    imgNegatives = "global/figures/negatives/neg-eco-"
    imgLabels = "global/figures/labels/label_"
    imgNumbers = "global/figures/prices/n_"
    imgPrices = "global/figures/prices/n_"
    imgTrueprice = "global/figures/prices/n_"
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
PARTICIPANT_FIELDS = ['lPos', 'iSelectedTrial', 'trials', 'bChoseA', 'sTreatment']


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

            # Initialize bChoseA
            p.bChoseA = None

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
            player.Product1, player.Product2 = trial['products']

        player.P1, player.P2, player.S1, player.S2, player.Q1, player.Q2 = lValues


def generate_trials():
    # Initialize the combinations
    combinations = []

    # Define the price sets
    price_sets = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    sustainability_values = [1, 2, 3]
    credentials_values = [1, 2]  # Only two labels for credentials
    product_pairs = [(1, 2), (3, 4), (5, 6)]

    # Generate trials where one attribute changes at a time
    for _ in range(18):
        # Generate trials where only price changes
        for price_set in price_sets:
            P1 = random.choice(price_set)
            P2 = random.choice(price_set)
            while P1 == P2:
                P2 = random.choice(price_set)
            values = [P1, P2, 1, 1, 1, 1]
            products = random.choice(product_pairs)
            combinations.append({'values': values, 'condition': 'Prices', 'products': products})

        # Generate trials where only sustainability changes
        price_set = random.choice(price_sets)
        P1 = random.choice(price_set)
        P2 = P1  # Use the same price for both products
        S1 = random.choice(sustainability_values)
        S2 = random.choice(sustainability_values)
        while S1 == S2:
            S2 = random.choice(sustainability_values)
        values = [P1, P2, S1, S2, 1, 1]
        products = random.choice(product_pairs)
        combinations.append({'values': values, 'condition': 'Sustainability', 'products': products})

        # Generate trials where only credentials change
        price_set = random.choice(price_sets)
        P1 = random.choice(price_set)
        P2 = P1  # Use the same price for both products
        Q1 = random.choice(credentials_values)
        Q2 = random.choice(credentials_values)
        while Q1 == Q2:
            Q2 = random.choice(credentials_values)
        values = [P1, P2, 1, 1, Q1, Q2]
        products = random.choice(product_pairs)
        combinations.append({'values': values, 'condition': 'Credentials', 'products': products})

    # Shuffle combinations to ensure random order
    random.shuffle(combinations)

    return combinations


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
                if condition == "Trueprice":
                    lPaths.append(f"{C.imgTrueprice}{v}.png")
                elif condition == "Prices":
                    lPaths.append(f"{C.imgPrices}{v}.png")
                elif condition == "Numbers":
                    lPaths.append(f"{C.imgNumbers}{v}.png")
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


class Decision(Page):
    form_model = 'player'
    form_fields = ['sChoice']

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
        p = player.participant
        
        if player.round_number == p.iSelectedTrial:
            p.bChoseA = player.sChoice == 'A'  # Assuming 'A' is one of the choices


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


page_sequence = [SideButton, Decision, Confidence]

# Ensure that SESSION_CONFIGS includes the app
SESSION_CONFIGS = [
    dict(
        name='task',
        display_name='Task',
        num_demo_participants=1,
        app_sequence=['Task']
    ),
]
