RUN: test main
RUN-WITH-MYSQL: test-with-mysql main-with-mysql

WIN-RUN: wtest wmain
WIN-RUN-WITH-MYSQL: wtest-with-mysql wmain-with-mysql

test-with-mysql:
	.venv/bin/pytest tests/ -v

docker-build:
	docker build ./ -t mysql-dbc
	docker run --env="MYSQL_ROOT_PASSWORD=root_password" -p 3306:3306 -d mysql-dbc
	sleep 20

test:
	.venv/bin/pytest tests/json_to_agrt_main_test.py -v

main-with-mysql:
	.venv/bin/python ./main/json_format_push_to_mysql.py --db='presentation_db'

main: test
	.venv/bin/python ./main/json_format_push_to_mysql.py

wtest-with-mysql:
	.venv\Scripts\pytest .\tests -v

wtest:
	.venv\Scripts\pytest .\tests\json_to_agrt_main_test.py -v

wmain-with-mysql: wtest-with-mysql
	.venv\Scripts\python .\main\json_format_push_to_mysql.py --db='presentation_db'

wmain: wtest
	.venv\Scripts\python .\main\json_format_push_to_mysql.py
