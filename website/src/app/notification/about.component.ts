import { Component, OnInit, NgZone, ChangeDetectorRef } from '@angular/core';

import { environment } from '@env/environment';
import { ApiService } from '../core/api/ApiService';

@Component({
  selector: 'app-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.scss']
})
export class AboutComponent implements OnInit {
  version: string = environment.version;

  list: any[];
  constructor(public apiService: ApiService, private cdRef: ChangeDetectorRef) {}

  ngOnInit() {
    this.getNotifications();
  }

  getNotifications() {
    let that = this;
    this.apiService.getNotifications().subscribe((data: any) => {
      //console.log(data);
      data = data.sort((a: any, b: any) => {
        return new Date(b.createdOn).getTime() - new Date(a.createdOn).getTime();
      });
      //that.list = data;
      that.list = [];

      data.forEach(function(item: any) {
        item.signedUrl += '&random+=' + Math.random();
        that.list.push(item);
      });
      this.cdRef.detectChanges();
    });
  }

  deleteMessage(msg: any, index: number): void {
    let that = this;
    this.apiService.deleteNotification(msg.id, msg.createdOn).subscribe((data: any) => {
      that.list.splice(index, 1);
    });
  }

  indextFace(msg: any, index: number): void {
    console.log(msg);
    let that = this;
    let postData = {
      id: msg.id,
      createdOn: msg.createdOn,
      faceName: msg.faceName,
      key: msg.key
    };
    this.apiService.indexFace(postData).subscribe((data: any) => {
      //that.list.splice(index,1);
    });
  }
}
