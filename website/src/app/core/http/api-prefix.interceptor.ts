import { Injectable } from '@angular/core';
import { HttpEvent, HttpInterceptor, HttpHandler, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import { Credentials } from '../authentication/authentication.service';
const credentialsKey = 'credentials';
/**
 * Prefixes all requests with `environment.serverUrl`.
 */
@Injectable()
export class ApiPrefixInterceptor implements HttpInterceptor {
  private _credentials: Credentials | null;

  constructor() {
    const savedCredentials = sessionStorage.getItem(credentialsKey) || localStorage.getItem(credentialsKey);
    if (savedCredentials) {
      this._credentials = JSON.parse(savedCredentials);
    }
  }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    console.log('$$$$$ interceptor', request.url, this._credentials);
    request = request.clone({
      setHeaders: {
        Authorization: 'Basic ' + window.btoa(this._credentials.username + ':' + this._credentials.token)
      }
    });
    return next.handle(request);
  }
}
