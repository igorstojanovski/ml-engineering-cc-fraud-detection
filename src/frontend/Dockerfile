FROM node:18-alpine
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ARG VITE_OPENCAGE_TOKEN
ENV VITE_OPENCAGE_TOKEN=$VITE_OPENCAGE_TOKEN
ENV NODE_ENV=production

RUN npm run build

EXPOSE 5173
CMD ["npm", "run", "preview", "--", "--port", "5173", "--host"]