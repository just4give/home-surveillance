import { Injectable, NgModule } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { ApiService } from '../api/ApiService';
import { Credentials } from '../authentication/authentication.service';

const credentialsKey = 'credentials';

@Injectable()
export class SocketClient extends Socket {
  private _credentials: Credentials | null;

  constructor(apiService: ApiService) {
    let ngrok = apiService.getNgrok();

    let savedCredentials = sessionStorage.getItem(credentialsKey) || localStorage.getItem(credentialsKey);
    if (savedCredentials) {
      savedCredentials = JSON.parse(savedCredentials);
    }
    let token = window.btoa(savedCredentials['username'] + ':' + savedCredentials['token']);
    super({ url: ngrok + '/test', options: { query: { token: token } } });
  }
}
