
from reqlastrology import astrology_base, Field, AnyOf uuid, Whatever, UUID

Base = astrology_base()

class SideKick(Base):
    '''A Hero's sidekick'''

    id = Field(uuid)
    sidekick_name = Field(str)
    age = Field(int)
    metadata = Field(Maybe(object))
    whatever = Field(Whatever)
    

class SuperHero(Base):
    '''A really super kind of guy'''
    __table__ = 'super_heroes'

    hero_name = Field(str, id=True)
    superpower = Field(AnyOf('invisibility', 'flight', 'strength'))
    weakness = Field(AnyOf('toxic waste', 'the sea', 'pleather'))
    tookit = Field(Exactly(object, 
    real_name = Field(str)

    side_kick = SideKick
    nemesis = lambda: SuperVillain  # Need to lambda wrap for lazy resolution


class SuperVillain(Base):
    __table__ = 'super_villains'

    favorite_colors = [Field(Enum('orange', 'green', 'yellow'))]
    name = Field(max_length=35, id=True)
    age = Field(int)

    nemesis = SuperHero


SuperVillain.get(101)

SuperHero.filter(hero_name="Batman")
SuperHero.filter(SuperHero.sidekick.age > 15).all()