import { Component, OnInit } from '@angular/core';
import { finalize } from 'rxjs/operators';
import { OrderPipe } from 'ngx-order-pipe';
import { QuoteService } from './quote.service';
import { ApiService } from '../core/api/ApiService';
import { SocketClient } from '../core/socket/socket.client';
import { Router } from '@angular/router';
import { AuthenticationService } from '@app/core/authentication/authentication.service';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  quote: string;
  isLoading: boolean;
  editorMsg: string;
  msgList: any[] = [];
  toUser = {
    id: '101'
  };
  user = {
    id: '102'
  };
  constructor(
    public apiService: ApiService,
    private socketClient: SocketClient,
    private router: Router,
    public authenticationService: AuthenticationService,
    private orderPipe: OrderPipe
  ) {
    //this.msgList = this.orderPipe.transform(this.msgList, 'createdOn');
  }

  ngOnInit() {
    let auth = this.apiService.isAuthenticated();
    console.log('Auth = ' + auth);
    let that = this;
    this.socketClient.on('guest_event', (data: any) => {
      console.log('$$$ Message received ', data);
      if (!that.msgList) {
        that.msgList = [];
      }
      that.msgList.unshift(data);
    });
    // this.socketClient.fromEvent("guest_event")
    //           .map( (data:any) => {
    //             console.log(data);
    //            } );
  }

  sendMsg = function() {
    console.log('$$$ ' + this.editorMsg);
    this.socketClient.emit('owner_event', { data: this.editorMsg });

    this.msgList.unshift({
      createdOn: new Date(),
      message: this.editorMsg,
      source: 'owner',
      type: 'text'
    });
  };

  logout() {
    this.authenticationService.logout().subscribe(() => this.router.navigate(['/login'], { replaceUrl: true }));
  }

  loadMessages() {
    console.log('clicked');
    this.apiService.getMessages().subscribe((data: any) => {
      console.log(data);
      data = data.sort((a: any, b: any) => {
        return new Date(b.createdOn).getTime() - new Date(a.createdOn).getTime();
      });
      this.msgList = this.msgList.concat(data);
    });
  }

  deleteMessage(msg: any, index: number): void {
    let that = this;
    this.apiService.deleteMessage(msg.id, msg.createdOn).subscribe((data: any) => {
      that.msgList.splice(index, 1);
    });
  }
}
