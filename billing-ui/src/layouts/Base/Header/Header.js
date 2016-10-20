import React, {Component} from 'react';
import animate from 'gsap-promise';
import user from '~/user';

import './Header.scss';

const containerAnimationStates = {
  beforeEnter: {
    xPercent: '100%'
  },
  idle: {
    xPercent: '0'
  },
};

const elementAnimationStates = {
  beforeEnter: {
    opacity: 0,
    x: 20
  },
  idle: {
    opacity: 1,
    x: 0,
  },
};

export default class extends Component {
  componentDidMount () {
    this.initUIState();  
  }

  initUIState() {
    const elements = [this.refs.logo, this.refs.logout];
    return Promise.all([
      animate.set(this.refs.container, containerAnimationStates.beforeEnter),
      animate.set(elements, elementAnimationStates.beforeEnter),
    ]);
  }

  async animateIn() {
    const elements = [this.refs.logo, this.refs.logout];
    await animate.to(this.refs.container, 0.1, containerAnimationStates.idle);
    await animate.staggerTo(elements, 0.2, Object.assign(elementAnimationStates.idle, {clearProps: 'all'}), 0.1);
  }

  render() {
    return (
      <header className="Header" ref="container">
        <img
          ref="logo"
          className="logo"
          src={require('~/assets/images/logo-full.png')}
          alt="Cancer Genome COLLABORATORY"
        />

        <span
          ref="logout"
          className="logout"
          onClick={() => user.logout()}
        >Logout {user.username}</span>
      </header>
    );
  }
}