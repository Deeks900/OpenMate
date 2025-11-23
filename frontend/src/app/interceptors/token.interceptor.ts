//@Injectable() marks a class as available for injection by Angular’s DI system (so other classes can receive it in their constructors).
import { Injectable } from '@angular/core';
import {
  HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse
} from '@angular/common/http';
import { Observable, catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable()
export class TokenInterceptor implements HttpInterceptor {
  isRefreshing = false;  
  constructor(private auth: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {

    // Skip interception for these endpoints
    if (req.url.includes("/auth/login") ||
        req.url.includes("/auth/register") ||
        req.url.includes("/auth/refresh")) {
      return next.handle(req);
    }

    const token = this.auth.getToken();

    const request = token ? req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    }) : req;

    return next.handle(request).pipe(
      catchError((err: HttpErrorResponse) => {
        if (err.status === 401 && !this.isRefreshing) {
          this.isRefreshing = true;

          return this.auth.refreshToken().pipe(
            switchMap((newToken: string) => {
              this.isRefreshing = false;

              const retryReq = req.clone({
                setHeaders: { Authorization: `Bearer ${newToken}` }
              });

              return next.handle(retryReq);
            }),
            catchError(refreshErr => {
              this.isRefreshing = false;

              //REFRESH TOKEN EXPIRED → FORCE LOGOUT
              if (refreshErr.status === 401 || refreshErr.status === 403) {
                this.auth.logout();     // remove tokens, hit backend logout if needed
                window.location.href = "/login"; 
              }

              return throwError(() => refreshErr);
            })
          );
        }

        return throwError(() => err);
      })
    );
  }
}


//HttpInterceptor — interface your class implements to become an interceptor.
//HttpRequest<T> — represents an outgoing HTTP request (immutable).
//HttpHandler — object responsible for forwarding the request to the next handler in the chain.
//HttpEvent<T> — events produced during an HTTP call (response, progress, etc.).
