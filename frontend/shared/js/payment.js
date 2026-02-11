// Payment Service
function PaymentService() {
    this.baseUrl = '';
}

PaymentService.prototype.getSubscriptionPlans = function() {
    var _this = this;
    return new Promise(function(resolve, reject) {
        fetch(_this.baseUrl + '/payments/plans')
            .then(function(response) {
                if (!response.ok) {
                    response.json().then(function(error) {
                        reject(new Error(error.detail || 'Failed to fetch plans'));
                    }).catch(function() {
                        reject(new Error('Failed to fetch plans'));
                    });
                } else {
                    response.json().then(function(plans) {
                        resolve(plans);
                    }).catch(function(error) {
                        reject(error);
                    });
                }
            })
            .catch(function(error) {
                console.error('Get plans error:', error);
                reject(error);
            });
    });
};

PaymentService.prototype.initiatePayment = function(paymentData) {
    var _this = this;
    return new Promise(function(resolve, reject) {
        fetch(_this.baseUrl + '/payments/initiate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(paymentData)
        })
        .then(function(response) {
            if (!response.ok) {
                response.json().then(function(error) {
                    reject(new Error(error.detail || 'Failed to initiate payment'));
                }).catch(function() {
                    reject(new Error('Failed to initiate payment'));
                });
            } else {
                response.json().then(function(paymentResult) {
                    resolve(paymentResult);
                }).catch(function(error) {
                    reject(error);
                });
            }
        })
        .catch(function(error) {
            console.error('Initiate payment error:', error);
            reject(error);
        });
    });
};

PaymentService.prototype.subscribeToPlan = function(planId, userData) {
    var _this = this;
    return new Promise(function(resolve, reject) {
        fetch(_this.baseUrl + '/payments/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                plan_id: planId,
                user_email: userData.email,
                user_name: userData.name,
                user_phone: userData.phone
            })
        })
        .then(function(response) {
            if (!response.ok) {
                response.json().then(function(error) {
                    reject(new Error(error.detail || 'Failed to subscribe'));
                }).catch(function() {
                    reject(new Error('Failed to subscribe'));
                });
            } else {
                response.json().then(function(paymentResult) {
                    resolve(paymentResult);
                }).catch(function(error) {
                    reject(error);
                });
            }
        })
        .catch(function(error) {
            console.error('Subscribe error:', error);
            reject(error);
        });
    });
};

PaymentService.prototype.getPaymentStatus = function(orderId) {
    var _this = this;
    return new Promise(function(resolve, reject) {
        fetch(_this.baseUrl + '/payments/status/' + orderId)
            .then(function(response) {
                if (!response.ok) {
                    response.json().then(function(error) {
                        reject(new Error(error.detail || 'Failed to get status'));
                    }).catch(function() {
                        reject(new Error('Failed to get status'));
                    });
                } else {
                    response.json().then(function(status) {
                        resolve(status);
                    }).catch(function(error) {
                        reject(error);
                    });
                }
            })
            .catch(function(error) {
                console.error('Get payment status error:', error);
                reject(error);
            });
    });
};

PaymentService.prototype.openPaymentWindow = function(paymentUrl) {
    var popup = window.open(
        paymentUrl,
        'payment_window',
        'width=800,height=600,scrollbars=yes,resizable=yes'
    );
    
    if (!popup || popup.closed || typeof popup.closed == 'undefined') {
        window.location.href = paymentUrl;
    }
    
    return popup;
};

PaymentService.prototype.createPaymentButton = function(plan, userData) {
    var button = document.createElement('button');
    button.className = 'payment-button';
    button.textContent = 'Subscribe - $' + plan.price + '/month';
    button.style.cssText = 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; width: 100%;';
    
    var _this = this;
    button.addEventListener('click', function() {
        button.disabled = true;
        button.textContent = 'Processing...';
        
        _this.subscribeToPlan(plan.id, userData)
            .then(function(paymentResult) {
                _this.openPaymentWindow(paymentResult.payment_url);
            })
            .catch(function(error) {
                console.error('Payment error:', error);
                alert('Payment failed: ' + error.message);
                button.disabled = false;
                button.textContent = 'Subscribe - $' + plan.price + '/month';
            });
    });
    
    button.addEventListener('mouseenter', function() {
        if (!button.disabled) {
            button.style.transform = 'translateY(-2px)';
            button.style.boxShadow = '0 10px 25px rgba(102, 126, 234, 0.3)';
        }
    });
    
    button.addEventListener('mouseleave', function() {
        if (!button.disabled) {
            button.style.transform = 'translateY(0)';
            button.style.boxShadow = 'none';
        }
    });
    
    return button;
};

var paymentService = new PaymentService();
