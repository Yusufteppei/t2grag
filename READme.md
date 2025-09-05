## drawio - Architectural Diagram : https://drive.google.com/file/d/1A8zIRIS4GuDVSGMzNvI0myVE-xxx5prn/view?usp=drive_link

### Docker Compose file includes :
1. A Nextjs frontend client to chat with the AI
2. A Django backend that processes the uploaded files and serves the API
3. Grafana for visualization of usage analytics and AI system performance
4. Label Studio receives the response of each message sent to the AI to allow annotations
5. A postgres db for the backend


##	FOR SIMPLICITY AND TIME CONSTRAINT, THE FRONTEND WAS KEPT BASIC:
		ONLY ONE CHAT IS KEPT PER USER
		THE CONTEXT SENT TAKES THE MOST RECENT PART OF THE CHAT APPENDED TO THE SYSTEM PROMPT INSTEAD OF MORE SOPHISTICATED SUMMARIES

##	THE DJANGO DEFAULT ADMIN HANDLES THE FILES UPLOAD:
		On upload, the django app chunks the files and uses openai API to get their embeddings, sending them to pinecone to store


##	PINECONE HANDLES THE SIMILARITIES:
		Instead of manually comparing embeddings, pinecone returns the top k closest "chunks", in our case k=1. That chunk is sent as a part of
		the context including the system prompt and an excerpt of the on-going conversation

##	SOME GRAFANA PANELS READ DIRECTLY FROM THE BACKEND DB FOR USAGE METRICS
		There is a Usage model in the django app that stores latency and token data for each query sent from the frontend or directly to the api.
		
##	THE ANNOTATIONS DATA IS FETCHED FROM LABEL STUDIO USING THE PYTHON SDK WITHIN THE DJANGO BACKEND
		Due to the expiry of JWT tokens and the data wrangling limitation of grafana, the endpoint for reading the analytics of the annotations will be left open but throttled.
		In a production environment, it would be better to have a separate lightweight service for serving this data and then setting a firewall around it.
		
#	DEPLOYMENT  - DOCKER COMPOSE
	Extract docker-compose file from repo
	create .env file in the same directory
	Run docker compose:
		docker compose up

		
##	ENV
PINECONE_API_KEY=
PINECONE_INDEX_NAME=custom-gpt

OPENAI_API_KEY=

LABEL_STUDIO_API_KEY=
LABEL_STUDIO_URL=http://labelstudio:8887

NEXT_PUBLIC_URL=http://localhost:8005 or <BACKEND URL>
~                                       

#	LIVE DEPLOYMENT ON ..
https://api.t2grag.zaidyusuf.com
https://grafana.t2grag.zaidyusuf.com
https://labelstudio.t2grag.zaidyusuf.com
https://web.t2grag.zaidyusuf.com


##	IN PRODUCTION, IN ORDER TO PROTECT THE DATABASE GRAFANA COULD EITHER BE HOSTED WITHIN A PRIVATE NETWORK OR THE METRICS SHOULD BE EXPORTED
##	VIA A SEPARATE SERVICE LIKE PROMETHEUS BUT FOR DEMONSTRATION AND DEPLOYMENT SIMPLICITY, IT WILL BE LEFT OPEN.
