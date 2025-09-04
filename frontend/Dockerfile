# -------- Stage 1: Build --------
    FROM node:20.15.1-slim AS builder

    # Set working directory
    WORKDIR /app
    
    # Install dependencies based on lockfile
    COPY package*.json ./
    RUN npm install --frozen-lockfile
    
    # Copy all project files
    COPY . .
    
    # Build the Next.js project
    RUN npm run build
    
    # -------- Stage 2: Run --------
    FROM node:20.15.1-slim AS runner
    
    WORKDIR /app
    
    # Ensure production environment
    ENV NODE_ENV=production
    
    # Copy only necessary files from builder
    COPY --from=builder /app/package*.json ./
    COPY --from=builder /app/node_modules ./node_modules
    COPY --from=builder /app/.next ./.next
    COPY --from=builder /app/public ./public
    COPY --from=builder /app/next.config.mjs ./next.config.mjs
    
    # Expose Next.js port
    EXPOSE 3000
    
    # Run Next.js
    CMD ["npm", "start"]
    