import { Injectable, NgModule } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { ApiService } from '../api/ApiService';

@Injectable()
export class SocketClient extends Socket {

    constructor(apiService: ApiService) {
        let ngrok =   apiService.getNgrok();
        super({ url: ngrok+'/test', options: {'Authorization':'Basic QWRtaW46QWRtaW4='} });
    }

}