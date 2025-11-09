//@Injectable() marks a class as available for injection by Angular’s DI system (so other classes can receive it in their constructors).
import { Injectable } from '@angular/core';
import {
  HttpInterceptor, HttpRequest, HttpHandler, HttpEvent
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable()
export class TokenInterceptor implements HttpInterceptor {
  constructor(private auth: AuthService) {}

  //This is the required method for HttpInterceptor. It is called for every outgoing HTTP request.
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.auth.getToken();
    if (!token) return next.handle(req);

    //HttpRequest objects are immutable. Always use req.clone({...}) to modify headers, body, params, etc.
    const cloned = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });

    return next.handle(cloned);
  }
}

//HttpInterceptor — interface your class implements to become an interceptor.
//HttpRequest<T> — represents an outgoing HTTP request (immutable).
//HttpHandler — object responsible for forwarding the request to the next handler in the chain.
//HttpEvent<T> — events produced during an HTTP call (response, progress, etc.).
