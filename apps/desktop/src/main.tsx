import '@vh/ui/tokens.css';
import '@vh/ui/fonts.css';
import './styles.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App.tsx';
import { ContentProvider } from './lib/content.tsx';
import { installExternalLinkHandler } from './lib/platform.ts';
import { UserDataProvider } from './lib/userdata.tsx';
import { VaultProvider } from './lib/vault.tsx';

// 外链（含 arena.ai 榜单）改走系统浏览器，避免 WebView 被 Cloudflare 硬拦
installExternalLinkHandler();

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
