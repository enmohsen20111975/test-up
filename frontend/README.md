# EngiSuite Analytics Pro - Frontend

Modern, responsive frontend for EngiSuite Analytics Pro SaaS platform.

## Features

### Pages
- **Landing Page** (`index.html`) - Main website with features, pricing, and CTA
- **Login** (`login.html`) - User authentication page
- **Register** (`register.html`) - New user registration
- **Dashboard** (`dashboard.html`) - Main dashboard with quick access and analytics
- **Calculators** (`calculators.html`) - 50 engineering calculators organized by category
- **Analytics** (`analytics.html`) - Data analysis module with file upload and visualization
- **AI Assistant** (`ai-assistant.html`) - Interactive chat interface with AI recommendations
- **Reports** (`reports.html`) - Report management and generation
- **Profile** (`profile.html`) - User profile and account settings

### Design Features
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Arabic Support**: Full RTL (right-to-left) layout for Arabic language
- **Modern UI**: Clean, professional design with smooth animations
- **Accessibility**: Semantic HTML and ARIA labels for screen readers
- **Performance**: Optimized CSS and JavaScript for fast loading

### Technologies Used
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with Grid, Flexbox, and animations
- **Vanilla JavaScript**: Lightweight, fast, and compatible
- **Font Awesome 6.0.0**: Beautiful vector icons
- **No Frameworks**: Keep it simple and fast

## Getting Started

### Local Development

1. **Serve the frontend**:
   ```bash
   # Using Python's built-in server
   python -m http.server 8001

   # Or using Node.js http-server
   npm install -g http-server
   http-server -p 8001
   ```

2. **Access the frontend**:
   Open your browser and navigate to: `http://localhost:8001`

### Development Workflow

1. **Modify HTML Files**: Edit any of the `.html` files in the frontend directory
2. **CSS Changes**: Modify styles in `shared/css/engisuite-theme.css`
3. **JavaScript Changes**: Add functionality in `shared/js/auth.js` or `shared/js/ai-service.js`
4. **Refresh Browser**: Changes will be visible immediately when you refresh the page

## Project Structure

```
frontend/
├── index.html              # Landing page
├── login.html              # Login page
├── register.html           # Registration page
├── dashboard.html          # Main dashboard
├── calculators.html        # Engineering calculators
├── analytics.html          # Data analysis
├── ai-assistant.html       # AI chat interface
├── reports.html            # Reports management
├── profile.html            # User profile
└── shared/
    ├── css/
    │   └── engisuite-theme.css    # Main stylesheet
    └── js/
        ├── auth.js          # Authentication service
        └── ai-service.js    # AI integration
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance Optimizations

- **Minified CSS/JS**: Production-ready with minimal file sizes
- **Lazy Loading**: Images and content load as needed
- **CDN**: Fonts and icons from Cloudflare CDN
- **Compressed Assets**: Gzip compression for CSS and JavaScript
- **Responsive Images**: Serve appropriate sizes for different devices

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to your branch: `git push origin feature/your-feature`
7. Submit a pull request

## License

MIT License - See LICENSE file