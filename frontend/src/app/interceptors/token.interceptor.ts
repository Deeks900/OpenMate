//@Injectable() marks a class as available for injection by Angular’s DI system (so other classes can receive it in their constructors).
import { Injectable } from '@angular/core';
import {
  HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse
} from '@angular/common/http';
import { Observable, catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable()
export class TokenInterceptor implements HttpInterceptor {
  constructor(private auth: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
     // Skip refresh logic for login, register, refresh endpoints
    if (req.url.includes("/auth/login") ||
        req.url.includes("/auth/register") ||
        req.url.includes("/auth/refresh")) {
      return next.handle(req);
    }

    const token = this.auth.getToken();

    const cloned = token ? req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    }) : req;

    return next.handle(cloned).pipe(
      catchError((err: HttpErrorResponse) => {
        if (err.status === 401) {
          console.log("I am in interceptor")
          return this.auth.refreshToken().pipe(
            switchMap((newToken: string) => {
              const retryReq = req.clone({
                setHeaders: { Authorization: `Bearer ${newToken}` }
              });
              return next.handle(retryReq);
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
