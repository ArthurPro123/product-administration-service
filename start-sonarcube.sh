
# docker run --name postgres_for_sonarqube  \
# 	-d  \
# 	-e POSTGRES_USER=sonar  \
# 	-e POSTGRES_USER=postgres  \
# 	-e POSTGRES_PASSWORD=Test12345  \
# 	-p 5432:5432  \
# 	-v postgres_data:/var/lib/postgresql/data  \
# 	--network sonarqube_network  \
# 	postgres:alpine

# sleep 10

docker run --name sonarqube  \
	-d  \
	-p 9000:9000  \
	-e sonar.jdbc.url=jdbc:postgresql://postgres/postgres  \
	-e sonar.jdbc.username=sonar  \
	-e sonar.jdbc.password=Test12345  \
	 --network sonarqube_network  \
  -v sonarqube_data:/opt/sonarqube/data \
	 sonarqube

docker ps


# alias sonar-scanner=' \
# pysonar \
#   --sonar-host-url=http://localhost:9000 \
#   --sonar-token=... \
#   --sonar-project-key=testing_part_11
# '

# sonar-scanner

# firefox http://localhost:9000
