import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { TokenInterceptor } from './interceptors/token.interceptor';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    // Add this line to enable interceptors from Dependency Injector
    provideHttpClient(withInterceptorsFromDi()),

    // Register TokenInterceptor: This tells that this TokenInterceptor class is an Interceptor that is automatically applied to every Http requests 
    {
      provide: HTTP_INTERCEPTORS,
      useClass: TokenInterceptor,
      //Tells that this application can have multiple interceptors 
      multi: true
    }
  ]
};
