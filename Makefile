-include .env

test :; pytest -s

update-abi :; cp ../Basin/out/IBasin.sol/IBasin.json ./abi/.

mongodb-start :;  brew services start mongodb-community@6.0

mongodb-stop :; brew services stop mongodb-community@6.0