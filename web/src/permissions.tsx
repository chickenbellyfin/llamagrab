/**
 * methods to check permissions in the UI
 * actual permissions should be enforced in the API
 */

import { User } from "./api";

function isUserSuper(user: User | undefined): boolean {
  return user?.tier === 'super'
}

function isUserAdmin(user: User | undefined): boolean {
  return isUserSuper(user) || user?.tier === 'admin'
}

function isUserVerified(user: User | undefined): boolean {
  return isUserAdmin(user) || user?.tier === 'verified'
}

export class AuthPermissions {
  readonly user: User | undefined

  constructor(user: User | undefined) {
    this.user = user
  }
  
  
  isSuper(): boolean {
    return isUserSuper(this.user)
  }

  isAdmin(): boolean {
    return isUserAdmin(this.user)
  }

  isVerified(): boolean {
    return isUserVerified(this.user)
  }

  canVerifyUser(other: User): boolean {    
    return this.isAdmin() && other.tier === 'unverified'
  }

  canDeleteUser(other: User): boolean {
    return this.isSuper() && this.user?.id !== other.id
  }

  canResetPassword(other: User): boolean {

    return this.isSuper() || !isUserAdmin(other)
  }

  canMakeAdmin(other: User): boolean {
    return this.isSuper() && other.tier === 'verified'
  }
  
  canRemoveAdmin(other: User): boolean {
    return this.isSuper() && other.tier === 'admin'
  }

}


// interface Permissions {
//   canVerifyUser: (other: User) => boolean
//   canDeleteUser: (other: User) => boolean
//   canResetPassword: (other: User) => boolean
//   canMakeAdmin: (other: User) => boolean
//   canRemoveAdmin: (other: User) => boolean
// }

export function getPermissions(user: User | undefined): AuthPermissions {
  return new AuthPermissions(user);
}