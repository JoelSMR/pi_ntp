#Quick Explanation 
# Were gonna use one brand-new tool called UV
# So we need to specify at the Image ->How2InstallUV


# Pulls the image to work with
FROM python:3.13.9-alpine3.21 AS builder

WORKDIR /app

#We copy the requirements holder file, this because the docker layer way
#This to cache it properly 
COPY requirements.txt .

#Execute 2 commands inline
#Run the curl installation of the BrandNew UV, and inline we download the dependencies
RUN apk add curl &&\
    curl -LsSf https://astral.sh/uv/install.sh | sh &&\
    uv add -r requirements.txt &&\
    uv add pyinstaller
#     -r == --requirements (means pathfile)

#Copy * the Dockerfile-Host Directory into the Container Dir Given
#Except the ones in .dockerignore file
COPY . .

# Compila binario single-file  
RUN uv run pyinstaller --onefile --name mi_app ./src/mi_app/launcher.py

# Pulls the image to work with
FROM alpine3.21 AS runner

#This verb execute the creation and recolocation in a directory
#Used for setting the 'root' of the contenerized apps
WORKDIR /app

#Establish Expecteds args
ARG GEMINI_API_KEY
ARG API_BACKEND_URL

#Set the Expected args into ENV VARIABLES
ENV GEMINI_API_KEY=${GEMINI_API_KEY}\
    API_BACKEND_URL=${API_BACKEND_URL}

COPY --from=builder /app/dist/mi_app .

#Create a new User To Run App in It
#1->Create the System Group, to hold the NewUser
#2->Create the New System User and set the group that he belongs
#3->Re set the permissions, setting NewUser permisons to only App folder 
RUN addgroup --system appgroup &&\
    adduser --system --ingroup appgroup appuser &&\
    chown -R appuser:appgroup /app

#Changes user, starts using the given one
USER appuser

#CLAIMS THAT, WHEN DEPLOYED, MUST EXPOSE THE PORT GIVEN
EXPOSE 8501

#Execute Command
ENTRYPOINT ["mi_app","--server.port=8501"]




