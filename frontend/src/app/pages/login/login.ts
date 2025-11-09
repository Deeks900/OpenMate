import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-login',
  imports: [
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    RouterModule
  ],
  templateUrl: './login.html',
  styleUrls: ['./login.css'],
})
export class Login {

  email = '';
  password = '';

  constructor(private auth: AuthService, private router: Router) {}

  login() {
    const payload = { email: this.email, password: this.password };

    this.auth.login(payload).subscribe({
      next: (res: any) => {
        localStorage.setItem('token', res.access_token);
        this.router.navigate(['/dashboard']);
      },
      error: err => alert(err.error.detail || "Login failed")
    });
  }
}
