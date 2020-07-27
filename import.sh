echo "Runing import script"
# users crud
curl -X PUT "http://localhost:81/users/1" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "email=daniel%40gmail.com&name=Daniel"
curl -X PUT "http://localhost:81/users/2" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "email=gimy%40gmail.com&name=Gimy"
curl -X PUT "http://localhost:81/users/3" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "email=tor%40gmail.com&name=Tor"

# fulltext search
curl -X PUT "http://localhost:82/fulltext" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "expression=Who%20has%20many%20apples%3F"
curl -X PUT "http://localhost:82/fulltext" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "expression=The%20apple%20tree%20grew%20in%20the%20park"
curl -X PUT "http://localhost:82/fulltext" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "expression=Some%20apples%20are%20green%20some%20are%20yellow"
curl -X PUT "http://localhost:82/fulltext" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "expression=How%20many%20trees%20are%20there%20in%20this%20forest%3F"