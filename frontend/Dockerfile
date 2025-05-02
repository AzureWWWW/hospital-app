# === Frontend (Angular) Build ===
FROM node:22-slim as build
WORKDIR /HospitalApp/frontend
COPY . .

RUN npm cache clean --force && npm install

EXPOSE 4200
CMD ["npm", "start"]