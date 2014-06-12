
from reqlastrology import *


Base = astrology_base(db_name='astro')

class MeatSalad(Base):
    __tablename__ = 'meat_salads'

    meat_salad_id = Field(str, primary_key=True)
    ham = Field(bool)
    numbers = Field([int], required=False)
    organic = Field(Nullable(bool))


if __name__ == '__main__':
    ms1 = MeatSalad(meat_salad_id='ameat')

    print repr(ms1)
    ms2 = MeatSalad.from_json({
        'meat_salad_id': 'just_ham',
        'ham': True,
        'numbers': [1,2,3],
    })
    print repr(ms2)

    try:
        ms1.numbers = ['a', 'b', 'c']
    except Exception as e:
        print e

    connection = r.connect().repl()
    Base.database.create_all()
    session = Session(Base.database, connection)
    session.add(ms1, ms2)
    new_object = session.query(MeatSalad).get('ameat')
    session.commit()

# Base = astrology_base()

# class SideKick(Base):
#     '''A Hero's sidekick'''

#     id = Field(uuid)
#     sidekick_name = Field(str)
#     age = Field(int)
#     metadata = Field(Maybe(object))
#     whatever = Field(Whatever)
    

# class SuperHero(Base):
#     '''A really super kind of guy'''
#     __table__ = 'super_heroes'

#     hero_name = Field(str, id=True)
#     superpower = Field(AnyOf('invisibility', 'flight', 'strength'))
#     weakness = Field(AnyOf('toxic waste', 'the sea', 'pleather'))
#     tookit = Field(Exactly(object))
#     real_name = Field(str)

#     side_kick = SideKick
#     nemesis = lambda: SuperVillain  # Need to lambda wrap for lazy resolution


# class SuperVillain(Base):
#     __table__ = 'super_villains'

#     favorite_colors = [Field(Enum('orange', 'green', 'yellow'))]
#     name = Field(max_length=35, id=True)
#     age = Field(int)

#     nemesis = SuperHero


# SuperVillain.get(101)

# SuperHero.filter(hero_name="Batman")
# SuperHero.filter(SuperHero.sidekick.age > 15).all()


# class Hero(Base):

#     hero = Field(str)
#     name = Field(str)
#     aka = Field(Maybe([str]))
#     magazine_titles = Field([str])
#     appearances_count = Field(int)
#     nemesis = lambda: Hero



# session = new_session()


# magneto = Hero(
#     hero="Magneto",
#     name="Max Eisenhardt",
#     aka=[
#         "Magnus",
#         "Erik Lehnsherr",
#         "Lehnsherr"
#     ], 
#         magazine_titles=[
#             "Alpha Flight",
#             "Avengers",
#             "Avengers West Coast",
#         ]
#         appearances_count=4
# )

# professor_x = Hero(   
#     hero="Professor Xavier",
#     name="Charles Francis Xavier",
#     magazine_titles=[
#         "Alpha Flight",
#         "Avengers",
#             "Bishop",
#         "Defenders",
#     ]
#     appearances_count=7
# )

# storm = Hero(
#     hero="Storm",
#     name="Ororo Monroe",
#     magazine_titles=[
#         "Amazing Spider-Man vs. Wolverine",
#         "Excalibur",
#         "Fantastic Four",
#         "Iron Fist",
#     ]
#         appearances_count=7
# )

# session.add()