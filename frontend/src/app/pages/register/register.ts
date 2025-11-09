import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatSelectModule } from '@angular/material/select';
import { MatOptionModule } from '@angular/material/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-register',
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatSelectModule,
    MatOptionModule,
    RouterModule
  ],
  templateUrl: './register.html',
  styleUrls: ['./register.css'],
})
export class Register {

  name = '';
  email = '';
  password = '';
  role = 'mentee';

  constructor(private auth: AuthService, private router: Router) {}

  register() {
    const payload = { name: this.name, email: this.email, password: this.password, role: this.role };

    this.auth.register(payload).subscribe({
      next: () => this.router.navigate(['/login']),
      error: err => alert(err.error.detail || "Registration failed")
    });
  }
}
