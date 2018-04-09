from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_project import Base, Catalog, Items, User

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
user1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user1)
session.commit()

# Item in catalog
# Cricket
catalog1 = Catalog(name = "Cricket")
session.add(catalog1)
session.commit()

items1 = Items(name = "Bat", description = "A cricket bat is a specialised piece of equipment used by batsmen in the sport of cricket to hit the ball, typically consisting of a cane handle attached to a flat-fronted willow-wood blade. The length of the bat may be no more than 38 inches (965 mm) and the width no more than 4.25 inches (108 mm). Its use is first mentioned in 1624. Since 1979, the rule change stipulated that bats can only be made from wood.", catalog = catalog1)
session.add(items1)
session.commit()

item2 = Items(name = "Ball", description = "A cricket ball is a hard, solid ball used to play cricket. A cricket ball consists of cork covered by leather, and manufacture is regulated by cricket law at first-class level. The manipulation of a cricket ball, through employment of its various physical properties, is a staple component of bowling and dismissing batsmen", catalog = catalog1)
session.add(item2)
session.commit()

# Football
catalog2 = Catalog(name = "Football")
session.add(catalog2)
session.commit()

item1 = Items(name = "Football", description = "A football is a ball inflated with air that is used to play one of the various sports known as football. In these games, with some exceptions, goals or points are scored only when the ball enters one of two designated goal-scoring areas; football games involve the two teams each trying to move the ball in opposite directions along the field of play", catalog = catalog2)
session.add(item1)
session.commit()

# Badminton
catalog3 = Catalog(name = "Badminton")
session.add(catalog3)
session.commit()

item1 = Items(name = "Racquet", description = "A racket or racquet[1] is a sports implement consisting of a handled frame with an open hoop across which a network of strings or catgut is stretched tightly. It is used for striking a ball or shuttlecock in games such as squash, tennis, racquetball, and badminton", catalog = catalog3)
session.add(item1)
session.commit()

item2 = Items(name = "Shuttlecock", description = "A shuttlecock (also called a bird or birdie) is a high-drag projectile used in the sport of badminton. It has an open conical shape formed by feathers (or a synthetic alternative) embedded into a rounded cork (or rubber) base", catalog = catalog3)
session.add(item2)
session.commit()


print "added sports items"
