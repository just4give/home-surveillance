import { BrowserModule } from '@angular/platform-browser';
import { ErrorHandler, NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { TranslateModule } from '@ngx-translate/core';
import { IonicApp, IonicErrorHandler, IonicModule } from 'ionic-angular';

import { CoreModule } from '@app/core';
import { SharedModule } from '@app/shared';
import { HomeModule } from './home/home.module';
import { ShellModule } from './shell/shell.module';

import { LoginModule } from './login/login.module';
import { SettingsModule } from './settings/settings.module';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { OrderModule, OrderPipe } from 'ngx-order-pipe';
import { AboutModule } from './notification/about.module';

@NgModule({
  imports: [
    BrowserModule,
    OrderModule,
    FormsModule,
    HttpClientModule,
    TranslateModule.forRoot(),
    IonicModule.forRoot(AppComponent, { locationStrategy: 'path' }),
    CoreModule,
    SharedModule,
    ShellModule,
    HomeModule,
    SettingsModule,
    AboutModule,
    LoginModule,
    AppRoutingModule // must be imported as the last module as it contains the fallback route
  ],
  exports: [OrderPipe],
  declarations: [AppComponent],
  providers: [{ provide: ErrorHandler, useClass: IonicErrorHandler }],
  bootstrap: [IonicApp]
})
export class AppModule {}
