# Story Generation SaaS - Frontend

A modern React frontend for the Story Generation SaaS application with dark mode UI, persistent authentication, and real-time story generation.

## Features

- **Modern UI**: Dark mode with glassmorphism design and animated backgrounds
- **Persistent Authentication**: JWT-based auth with automatic token refresh
- **Real-time Story Generation**: Interactive story creation with progress feedback
- **Dashboard**: User management, API key creation, and usage analytics
- **Story History**: View and manage previously generated stories
- **Responsive Design**: Mobile-friendly interface with smooth animations

## Technology Stack

- **React 18** with TypeScript for type safety
- **React Router** for client-side navigation
- **Context API** for global state management
- **Custom CSS** with advanced animations and effects
- **Local Storage** for persistent authentication
- **Fetch API** for backend communication

## Getting Started

### Prerequisites
- Node.js 16 or higher
- npm or yarn package manager
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The application will open at `http://localhost:3000`

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder. The build is minified and optimized for best performance.

### `npm test`

Launches the test runner in interactive watch mode.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

## Project Structure

```
src/
├── components/
│   ├── Auth/
│   │   ├── Auth.css           # Authentication styling
│   │   ├── Login.tsx          # Login component
│   │   └── Signup.tsx         # Signup component
│   ├── Dashboard/
│   │   ├── Dashboard.css      # Dashboard styling
│   │   └── Dashboard.tsx      # Main dashboard
│   ├── StoryGenerator/
│   │   ├── StoryGenerator.css # Story generation styling
│   │   └── StoryGenerator.tsx # Story creation interface
│   └── Common/
│       └── PrivateRoute.tsx   # Protected route wrapper
├── context/
│   └── AuthContext.tsx        # Authentication context
├── App.tsx                    # Main application component
├── App.css                    # Global styles and animations
└── index.tsx                  # Application entry point
```

## Key Features

### Authentication System
- **JWT Token Management**: Automatic refresh and validation
- **Persistent Sessions**: Users stay logged in across browser sessions
- **Protected Routes**: Automatic redirect for unauthenticated users
- **Loading States**: Smooth authentication initialization

### Dashboard Features
- **User Profile**: Email display and credit balance
- **API Key Management**: Create, view, and delete API keys
- **Usage History**: View previously generated stories with search
- **Story Viewer**: Modal to view full story content with copy functionality

### Story Generator
- **Interactive Form**: Prompt input with style selection
- **Real-time Generation**: Progress indicators and loading states
- **Result Display**: Formatted story output with scrollable text
- **Error Handling**: User-friendly error messages and retry options

### UI/UX Features
- **Dark Mode**: Consistent dark theme throughout the application
- **Glassmorphism**: Modern translucent card designs
- **Animations**: Smooth transitions and background effects
- **Responsive**: Mobile-first design with breakpoints

## API Integration

### Backend Endpoints
```typescript
// Authentication
POST /auth/login    - User login
POST /auth/signup   - User registration
POST /auth/refresh  - Token refresh
GET  /auth/me       - User profile

// Story Generation
POST /v1/story/generate - Generate story
GET  /v1/me/credits     - Get credits
GET  /v1/me/usage       - Get usage history

// API Keys
POST   /api-keys        - Create API key
GET    /api-keys        - List API keys
DELETE /api-keys/{id}   - Delete API key
```

## State Management

### AuthContext
- **User State**: Current user information and authentication status
- **Token Management**: Access and refresh token handling
- **Loading States**: Authentication initialization and API calls
- **Auto-refresh**: Automatic token renewal before expiration

## Environment Variables

Create `.env` file in the client directory:
```env
REACT_APP_API_URL=http://localhost:8000
```

## Learn More

- [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [React documentation](https://reactjs.org/)
