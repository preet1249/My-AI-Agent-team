# AI Agent Team Mobile App

React Native mobile app built with Expo for iOS and Android.

## Getting Started

### Prerequisites
- Node.js 18+
- pnpm (or npm)
- Expo CLI
- For iOS: Xcode and CocoaPods
- For Android: Android Studio

### Installation

```bash
# Install dependencies
pnpm install

# Start development server
pnpm start

# Run on Android
pnpm android

# Run on iOS
pnpm ios
```

### Testing on Device

1. Install Expo Go from App Store (iOS) or Play Store (Android)
2. Run `pnpm start`
3. Scan QR code with your device
4. App will load instantly

### Building for Production

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Build for Android
eas build --platform android

# Build for iOS
eas build --platform ios
```

## Features

- ✅ Dark theme optimized
- ✅ Poppins font family
- ✅ Chat interface
- ✅ Bottom tab navigation
- ✅ @ mention system (coming soon)
- ✅ Image upload (coming soon)
- ✅ Push notifications (coming soon)

## Folder Structure

```
apps/mobile/
├── app/                 # Expo Router pages
│   ├── (tabs)/         # Tab navigator
│   │   ├── index.tsx   # Chat screen
│   │   ├── sheets.tsx  # Sheets screen
│   │   ├── calendar.tsx # Calendar screen
│   │   ├── history.tsx # History screen
│   │   └── settings.tsx # Settings screen
│   └── _layout.tsx     # Root layout
├── assets/             # Images, fonts, icons
├── components/         # Reusable components
├── lib/               # Utilities
├── app.json           # Expo configuration
└── package.json       # Dependencies
```

## Notes

- Fonts need to be downloaded separately (Poppins family)
- Assets (icon, splash) need to be created
- Add fonts to `assets/fonts/` directory
