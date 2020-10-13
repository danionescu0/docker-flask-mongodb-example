#!/usr/bin/env bash

echo "Runing import script"
# random_demo
curl -X PUT "http://localhost:800/random" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "lower=10&upper=100"
curl -X PUT "http://localhost:800/random" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "lower=10&upper=100"
curl -X PUT "http://localhost:800/random" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "lower=10&upper=100"
curl -X PUT "http://localhost:800/random" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "lower=10&upper=100"
curl -X PUT "http://localhost:800/random" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "lower=10&upper=100"

# users crud
curl -X PUT "http://localhost:81/users/1" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "email=daniel%40gmail.com&name=Daniel"
curl -X PUT "http://localhost:81/users/2" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "email=gimy%40gmail.com&name=Gimy"
curl -X PUT "http://localhost:81/users/3" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "email=tor%40gmail.com&name=Tor"

# fulltext search
curl -X PUT "http://localhost:82/fulltext" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "expression=Who%20has%20many%20apples%3F"
curl -X PUT "http://localhost:82/fulltext" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "expression=The%20apple%20tree%20grew%20in%20the%20park"
curl -X PUT "http://localhost:82/fulltext" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "expression=Some%20apples%20are%20green%20some%20are%20yellow"
curl -X PUT "http://localhost:82/fulltext" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "expression=How%20many%20trees%20are%20there%20in%20this%20forest%3F"

# geolocation-search
curl -X POST "http://localhost:83/location" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "name=Bucharest&lat=44.2218653&lng=26.1753655"
curl -X POST "http://localhost:83/location" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "name=Sofia&lat=42.6954108&lng=23.2539076"
curl -X POST "http://localhost:83/location" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "name=Belgrade&lat=44.8152239&lng=20.3525579"
curl -X POST "http://localhost:83/location" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "name=Minsk&lat=53.8846196&lng=27.5233296"

# baesian
curl -X POST "http://localhost:84/item/1" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "name=Dan"
curl -X POST "http://localhost:84/item/2" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "name=John"
curl -X POST "http://localhost:84/item/3" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "name=Cicero"

curl -X PUT "http://localhost:84/item/vote/1" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "mark=6&userid=1"
curl -X PUT "http://localhost:84/item/vote/2" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "mark=8&userid=1"
curl -X PUT "http://localhost:84/item/vote/3" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "mark=9&userid=1"
curl -X PUT "http://localhost:84/item/vote/1" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "mark=8&userid=2"
curl -X PUT "http://localhost:84/item/vote/2" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "mark=8&userid=2"
curl -X PUT "http://localhost:84/item/vote/3" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "mark=4&userid=3"
curl -X PUT "http://localhost:84/item/vote/1" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "mark=4&userid=3"
curl -X PUT "http://localhost:84/item/vote/2" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "mark=9&userid=3"

# bookcollection
curl -X PUT "http://localhost:86/book/978-0735211292" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"isbn\": \"978-0735211292\", \"name\": \"Atomic Habits: An Easy & Proven Way to Build Good Habits & Break Bad Ones\", \"author\": \"James Clear\", \"publisher\": \"Avery; Illustrated Edition (October 16, 2018)\", \"nr_available\": 5}"
curl -X PUT "http://localhost:86/book/978-0525538585" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"isbn\": \"978-0525538585\", \"name\": \"Stillness Is the Key\", \"author\": \"Ryan Holiday\", \"publisher\": \"Portfolio (October 1, 2019)\", \"nr_available\": 3}"
curl -X PUT "http://localhost:86/borrow/1" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"id\": \"string\", \"userid\": 1, \"isbn\": \"978-0735211292\", \"borrow_date\": \"2020-10-13T13:04:37.644Z\", \"max_return_date\": \"2020-11-13T13:04:37.644Z\"}"