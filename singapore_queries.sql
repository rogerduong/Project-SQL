SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags 
	  UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key='postcode'
GROUP BY tags.value
ORDER BY count DESC;


#Show the entries with w 5-digit postal code 
SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags 
	  UNION ALL 
      SELECT * FROM ways_tags) as tags
WHERE tags.key='postcode' AND
LENGTH(tags.value) <> 6
GROUP BY tags.value;

#Results
38970,1
39594,1
39802,1
49965,1
50032,1
59817,1
79027,1
79903,1
88752,1
98585,1

#Sort cities by count
SELECT tags.key, tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key = 'city'
GROUP BY tags.value
ORDER BY count DESC;

#Results
city,Singapore,1444
city,#01-05,1
city,singapore,1

#List all tags
SELECT tags.key, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
GROUP BY tags.key
ORDER BY count DESC;

SELECT *
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key = "zu";

SELECT *
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.id = "424313428";

#List top 20 tags
SELECT tags.key, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
GROUP BY tags.key
ORDER BY count DESC
LIMIT 20;


#Number of unique users
SELECT COUNT(DISTINCT(e.uid))          
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e;

#Top 10 contributing users
SELECT e.user, COUNT(e.user) as contrib
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) as e
GROUP BY e.user
ORDER BY contrib DESC
LIMIT 10;

#Results
JaLooNz,275589
cboothroyd,50194
Luis36995,38471
ridixcr,38004
calfarome,32845
rene78,29926
nikhilprabhakar,22755
yurasi,20454
jaredc,19039
dmastin82,16963

#List amenities
SELECT tags.key, tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key = "amenity"
GROUP BY tags.value
ORDER BY count DESC
LIMIT 10;

#Results
amenity,restaurant,1755
amenity,parking,1689
amenity,atm,702
amenity,cafe,459
amenity,school,458
amenity,place_of_worship,381
amenity,fast_food,315
amenity,taxi,310
amenity,bank,230
amenity,swimming_pool,230

#Total number of restaurants
SELECT COUNT(*) as count 
FROM nodes_tags
    JOIN (SELECT DISTINCT(id)
    FROM nodes_tags
    WHERE nodes_tags.value = "restaurant") as nt
    ON nt.id = nodes_tags.id
WHERE nodes_tags.key = "cuisine";

#Results
636

#List top 10 cuisines of restaurants
SELECT nodes_tags.value, COUNT(*) as count 
FROM nodes_tags
    JOIN (SELECT DISTINCT(id)
    FROM nodes_tags
    WHERE nodes_tags.value = "restaurant") as nt
    ON nt.id = nodes_tags.id
WHERE nodes_tags.key = "cuisine"
GROUP BY nodes_tags.value
ORDER BY count DESC
LIMIT 20;

#Results
chinese,135
japanese,72
korean,44
pizza,43
italian,37
indian,35
asian,31
thai,29
french,15
seafood,13
burger,12
international,9
regional,9
vegetarian,6
vietnamese,6
western,6
american,5
chicken,5
indonesian,5
steak_house,5

#Total number of cafe
SELECT COUNT(*) as count 
FROM nodes_tags
    JOIN (SELECT DISTINCT(id)
    FROM nodes_tags
    WHERE nodes_tags.value = "cafe") as nt
    ON nt.id = nodes_tags.id
WHERE nodes_tags.key = "cuisine";

#Results
91

#List top 20 styles of cafe
SELECT nodes_tags.value, COUNT(*) as count 
FROM nodes_tags
    JOIN (SELECT DISTINCT(id)
    FROM nodes_tags
    WHERE nodes_tags.value = "cafe") as nt
    ON nt.id = nodes_tags.id
WHERE nodes_tags.key = "cuisine"
GROUP BY nodes_tags.value
ORDER BY count DESC
LIMIT 20;

coffee_shop,43
international,6
regional,4
sandwich,4
italian,3
Western,2
asian,2
coffee_shop;regional,2
french,2
"Hawker or Foodcourt, Chinese",1
Nanyang_Coffee,1
Western/Italian,1
acai,1
american;italian_pizza,1
breakfast;coffee_shop,1
cafe,1
cafe/diner,1
cake,1
chicken,1
coffee_shop;coffee,1

#Total number of fast-foods
SELECT COUNT(*) as count 
FROM nodes_tags
    JOIN (SELECT DISTINCT(id)
    FROM nodes_tags
    WHERE nodes_tags.value = "fast_food") as nt
    ON nt.id = nodes_tags.id
WHERE nodes_tags.key = "cuisine";

#Results
153

#List top 20 styles of fast-foods
SELECT nodes_tags.value, COUNT(*) as count 
FROM nodes_tags
    JOIN (SELECT DISTINCT(id)
    FROM nodes_tags
    WHERE nodes_tags.value = "fast_food") as nt
    ON nt.id = nodes_tags.id
WHERE nodes_tags.key = "cuisine"
GROUP BY nodes_tags.value
ORDER BY count DESC
LIMIT 20;

#Results
burger,59
chicken,27
sandwich,13
pizza,12
chinese,7
fast_food,5
ice_cream,5
asian,4
american,2
japanese,2
kebab,2
regional,2
"Curry Puffs",1
Fried_Chicken,1
Hawker_Centre,1
Sandwich,1
american;burger,1
burger;japanese,1
coffee_shop,1
fish;burger;breakfast;ice_cream;tea;cake;coffee_shop;american;chicken,1


#List top 10 sports
SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key = "sport"
GROUP BY tags.value
ORDER BY count DESC
LIMIT 10;

#Results
tennis,358
swimming,302
basketball,114
soccer,81
golf,32
multi,16
badminton,12
running,12
equestrian,7
yoga,7

#List top 10 leisure
SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key = "leisure"
GROUP BY tags.value
ORDER BY count DESC
LIMIT 10;

#Results
swimming_pool,944
pitch,804
park,475
playground,211
park_connector,80
sports_centre,72
fitness_centre,58
garden,41
fitness_station,33
recreation_ground,23

#List the places of worship
SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='place_of_worship') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='religion'
GROUP BY nodes_tags.value
ORDER BY num DESC
LIMIT 10;