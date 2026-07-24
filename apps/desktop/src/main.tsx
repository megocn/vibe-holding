import '@vh/ui/tokens.css';
import '@vh/ui/fonts.css';
import './styles.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App.tsx';
import { ContentProvider } from './lib/content.tsx';
import { UserDataProvider } from './lib/userdata.tsx';
import { VaultProvider } from './lib/vault.tsx';

const el = document.getElementById('root');
if (el) {
  createRoot(el).render(
    <StrictMode>
      <ContentProvider>
        <UserDataProvider>
          <VaultProvider>
            <App />
          </VaultProvider>
        </UserDataProvider>
      </ContentProvider>
    </StrictMode>,
  );
}
