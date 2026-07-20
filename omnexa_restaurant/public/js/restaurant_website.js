/* global frappe */
(function () {
	const STORAGE_LANG = "restaurant_site_lang";

	const DEFAULT_CATALOG = {
		menu: [
			{ key: "appetizers", name_ar: "مقبلات", name_en: "Appetizers", icon: "🥗", desc: "Fresh starters" },
			{ key: "mains", name_ar: "أطباق رئيسية", name_en: "Main Courses", icon: "🍽️", desc: "Signature dishes" },
			{ key: "desserts", name_ar: "حلويات", name_en: "Desserts", icon: "🍰", desc: "Sweet treats" },
			{ key: "drinks", name_ar: "مشروبات", name_en: "Beverages", icon: "🍹", desc: "Refreshing drinks" },
		],
		services: [
			{ icon: "📱", ar: "طلب أونلاين", en: "Online Ordering" },
			{ icon: "🚗", ar: "توصيل للمنزل", en: "Home Delivery" },
			{ icon: "🪑", ar: "حجز طاولات", en: "Table Reservation" },
			{ icon: "🎉", ar: "مناسبات خاصة", en: "Private Events" },
			{ icon: "👨‍🍳", ar: "طهاة محترفون", en: "Professional Chefs" },
			{ icon: "🌿", ar: "مكونات طازجة", en: "Fresh Ingredients" },
		],
	};

	window.RestaurantSite = {
		config: null,
		lang: localStorage.getItem(STORAGE_LANG) || "ar",
		page: "home",

		init(page) {
			this.page = page || "home";
			this.config = this.defaultConfig();
			this.applyTheme();
			this.renderChrome();
			this.loadConfig()
				.then(() => {
					this.applyTheme();
					this.renderChrome();
					const fn = this[`init_${this.page}`];
					if (typeof fn === "function") fn.call(this);
					this.setupReveal();
				})
				.catch(() => {
					this.config = this.config || this.defaultConfig();
					this.renderChrome();
					const fn = this[`init_${this.page}`];
					if (typeof fn === "function") fn.call(this);
					this.setupReveal();
				});
		},

		defaultConfig() {
			return {
				brand_name_ar: "Omnexa Restaurant",
				brand_name_en: "Omnexa Restaurant",
				tagline_ar: "تجربة طعام استثنائية",
				tagline_en: "Exceptional dining experience",
				hero_text_ar: "من المقبلات إلى الحلويات — قائمة متنوعة لكل ذوق",
				hero_text_en: "From appetizers to desserts — a diverse menu for every taste",
				hero_image: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1920&q=85",
				logo: "/assets/omnexa_restaurant/logo.png",
				primary_color: "#ff5722",
				secondary_color: "#e64a19",
				accent_color: "#00bcd4",
				gold_color: "#ffc107",
				menu: DEFAULT_CATALOG.menu,
				services: DEFAULT_CATALOG.services,
				stats: { dishes: 150, customers: 10000, locations: 5, years: 10 },
			};
		},

		t(key) {
			const map = {
				home: { ar: "الرئيسية", en: "Home" },
				menu: { ar: "القائمة", en: "Menu" },
				services: { ar: "الخدمات", en: "Services" },
				contact: { ar: "تواصل", en: "Contact" },
				login: { ar: "دخول", en: "Login" },
				order: { ar: "اطلب الآن", en: "Order Now" },
				learn_more: { ar: "اعرف المزيد", en: "Learn More" },
				dishes: { ar: "طبق", en: "Dishes" },
				customers: { ar: "عميل", en: "Customers" },
				locations: { ar: "موقع", en: "Locations" },
				years: { ar: "سنة", en: "Years" },
				loading: { ar: "جاري التحميل...", en: "Loading..." },
			};
			return (map[key] && map[key][this.lang]) || key;
		},

		esc(v) {
			if (typeof frappe !== "undefined" && frappe.utils && frappe.utils.escape_html) {
				return frappe.utils.escape_html(v == null ? "" : String(v));
			}
			const d = document.createElement("div");
			d.textContent = v == null ? "" : String(v);
			return d.innerHTML;
		},

		nameField() {
			return this.lang === "ar" ? "brand_name_ar" : "brand_name_en";
		},

		textField(base) {
			return this.lang === "ar" ? `${base}_ar` : `${base}_en`;
		},

		async loadConfig() {
			try {
				if (typeof frappe !== "undefined" && frappe.call) {
					const r = await frappe.call({
						method: "omnexa_restaurant.api.public_restaurant_site.get_site_config",
					});
					this.config = Object.assign(this.defaultConfig(), r.message || {});
				} else {
					const res = await fetch("/api/method/omnexa_restaurant.api.public_restaurant_site.get_site_config");
					const data = await res.json();
					this.config = Object.assign(this.defaultConfig(), data.message || {});
				}
			} catch (e) {
				this.config = this.config || this.defaultConfig();
			}
			if (this.config.primary_color) {
				document.documentElement.style.setProperty("--rest-primary", this.config.primary_color);
			}
			if (this.config.secondary_color) {
				document.documentElement.style.setProperty("--rest-secondary", this.config.secondary_color);
			}
			if (this.config.accent_color) {
				document.documentElement.style.setProperty("--rest-teal", this.config.accent_color);
			}
			if (this.config.gold_color) {
				document.documentElement.style.setProperty("--rest-gold", this.config.gold_color);
			}
		},

		applyTheme() {
			const root = document.querySelector(".restaurant-site");
			if (!root) return;
			root.dir = this.lang === "ar" ? "rtl" : "ltr";
			root.lang = this.lang;
		},

		toggleLang() {
			this.lang = this.lang === "ar" ? "en" : "ar";
			localStorage.setItem(STORAGE_LANG, this.lang);
			this.applyTheme();
			this.renderChrome();
			const fn = this[`init_${this.page}`];
			if (typeof fn === "function") fn.call(this);
		},

		setupReveal() {
			const els = document.querySelectorAll(".restaurant-reveal");
			if (!els.length || !("IntersectionObserver" in window)) {
				els.forEach((el) => el.classList.add("restaurant-visible"));
				return;
			}
			const obs = new IntersectionObserver(
				(entries) => {
					entries.forEach((e) => {
						if (e.isIntersecting) {
							e.target.classList.add("restaurant-visible");
							obs.unobserve(e.target);
						}
					});
				},
				{ threshold: 0.12 }
			);
			els.forEach((el) => obs.observe(el));
		},

		renderChrome() {
			const cfg = this.config || this.defaultConfig();
			const name = cfg[this.nameField()] || "Restaurant";
			const logo = cfg.logo
				? `<img src="${this.esc(cfg.logo)}" alt="" onerror="this.style.display='none'">`
				: "🍽️";
			const nav = [
				{ href: "/restaurant", key: "home", page: "home" },
				{ href: "/restaurant#restaurant-menu-section", key: "menu", page: "home" },
				{ href: "/restaurant#restaurant-services-section", key: "services", page: "home" },
				{ href: "/restaurant#restaurant-stats", key: "stats", page: "home" },
			];

			const header = document.getElementById("restaurant-header");
			if (header) {
				header.innerHTML = `
					<div class="restaurant-topbar"><div class="restaurant-wrap restaurant-topbar-inner">
						<span>📞 +966 11 000 0000</span>
						<span>✉ reservations@omnexa.restaurant</span>
						<span class="restaurant-topbar-links">
							<a href="/app/restaurant-workcenter">${this.lang === "ar" ? "مركز العمل" : "Workcenter"}</a>
							<a href="/app/restaurant-customer-portal">${this.lang === "ar" ? "بوابة العملاء" : "Customer Portal"}</a>
						</span>
					</div></div>
					<div class="restaurant-wrap restaurant-header-inner">
						<a class="restaurant-brand restaurant-brand-stack" href="/restaurant">
							<span class="restaurant-brand-logo">${logo}</span>
							<span class="restaurant-brand-name">${this.esc(name)}</span>
						</a>
						<button type="button" class="restaurant-mobile-toggle" id="restaurant-menu-toggle" aria-label="Menu">☰</button>
						<nav class="restaurant-nav restaurant-nav-single" id="restaurant-nav">
							<div class="restaurant-nav-links">
							${nav
								.map((n) => {
									const label = this.t(n.key);
									const active = n.page && this.page === n.page ? "active" : "";
									return `<a href="${n.href}" class="${active}">${label}</a>`;
								})
								.join("")}
							</div>
						</nav>
						<div class="restaurant-actions">
							<button type="button" class="restaurant-lang" id="restaurant-lang-toggle">${this.lang === "ar" ? "EN" : "AR"}</button>
							<a class="restaurant-btn restaurant-btn-outline" href="/login">${this.t("login")}</a>
							<a class="restaurant-btn restaurant-btn-primary" href="/app/restaurant-workcenter">${this.t("order")}</a>
						</div>
					</div>`;
				document.getElementById("restaurant-lang-toggle")?.addEventListener("click", () => this.toggleLang());
				document.getElementById("restaurant-menu-toggle")?.addEventListener("click", () => {
					document.getElementById("restaurant-nav")?.classList.toggle("open");
				});
			}

			const footer = document.getElementById("restaurant-footer");
			if (footer) {
				footer.innerHTML = `
					<div class="restaurant-wrap restaurant-footer-grid">
						<div>
							<h3>${this.esc(name)}</h3>
							<p>${this.esc(cfg[this.textField("hero_text")] || "")}</p>
							<p class="restaurant-footer-contact">📞 +966 11 000 0000 · ✉ reservations@omnexa.restaurant</p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "القائمة" : "Menu"}</h4>
							<p><a href="/restaurant#restaurant-menu-section">${this.lang === "ar" ? "مقبلات" : "Appetizers"}</a></p>
							<p><a href="/restaurant#restaurant-menu-section">${this.lang === "ar" ? "أطباق رئيسية" : "Main Courses"}</a></p>
							<p><a href="/restaurant#restaurant-menu-section">${this.lang === "ar" ? "حلويات" : "Desserts"}</a></p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "الخدمات" : "Services"}</h4>
							<p><a href="/restaurant#restaurant-services-section">${this.lang === "ar" ? "طلب أونلاين" : "Online Ordering"}</a></p>
							<p><a href="/restaurant#restaurant-services-section">${this.lang === "ar" ? "توصيل للمنزل" : "Home Delivery"}</a></p>
							<p><a href="/restaurant#restaurant-services-section">${this.lang === "ar" ? "حجز طاولات" : "Table Reservation"}</a></p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "البوابات" : "Portals"}</h4>
							<p><a href="/app/restaurant-workcenter">${this.lang === "ar" ? "مركز العمل" : "Workcenter"}</a></p>
							<p><a href="/app/restaurant-customer-portal">${this.lang === "ar" ? "بوابة العملاء" : "Customer Portal"}</a></p>
						</div>
					</div>
					<div class="restaurant-wrap restaurant-footer-bottom">© ${new Date().getFullYear()} ${this.esc(name)} · Omnexa · ErpGenEx</div>`;
			}
		},

		init_home() {
			const cfg = this.config || {};
			const heroImg = cfg.hero_image || "";
			const hero = document.getElementById("restaurant-hero");
			if (hero) {
				hero.innerHTML = `
					<div class="restaurant-hero-bg" style="background-image:url('${this.esc(heroImg)}')"></div>
					<div class="restaurant-hero-overlay"></div>
					<div class="restaurant-wrap restaurant-hero-premium-inner">
						<span class="restaurant-eyebrow restaurant-eyebrow-light">Omnexa Restaurant · Premium Dining</span>
						<h1>${this.esc(cfg[this.textField("tagline")] || "")}</h1>
						<p class="restaurant-hero-lead">${this.esc(cfg[this.textField("hero_text")] || "")}</p>
						<div class="restaurant-hero-cta">
							<a class="restaurant-btn restaurant-btn-accent" href="/app/restaurant-workcenter">${this.lang === "ar" ? "اطلب الآن" : "Order Now"}</a>
							<a class="restaurant-btn restaurant-btn-ghost-light" href="/restaurant#restaurant-menu-section">${this.lang === "ar" ? "استكشف القائمة" : "Explore Menu"}</a>
						</div>
					</div>`;
			}

			const trust = document.getElementById("restaurant-trust-strip");
			if (trust) {
				const values = (cfg.services || DEFAULT_CATALOG.services).slice(0, 5);
				trust.innerHTML = `<div class="restaurant-wrap restaurant-value-inner">${values
					.map((v) => `<div class="restaurant-value-item"><span>${v.icon}</span><strong>${this.lang === "ar" ? v.ar : v.en}</strong></div>`)
					.join("")}</div>`;
			}

			const menu = document.getElementById("restaurant-menu-section");
			if (menu) {
				const items = cfg.menu || DEFAULT_CATALOG.menu;
				menu.innerHTML = `
					<div class="restaurant-wrap">
						<div class="restaurant-section-title">
							<span class="restaurant-eyebrow">Our Menu</span>
							<h2>${this.lang === "ar" ? "قائمتنا الشهية" : "Our Delicious Menu"}</h2>
							<p>${this.lang === "ar" ? "مجموعة متنوعة من الأطباق المحضرة بحب من طهاة محترفين" : "A diverse range of dishes prepared with love by professional chefs"}</p>
						</div>
						<div class="restaurant-grid-4">${items
							.map((m) => `<div class="restaurant-card">
								<div style="font-size:48px;margin-bottom:16px;">${m.icon}</div>
								<h3>${this.esc(this.lang === "ar" ? m.name_ar : m.name_en)}</h3>
								<p>${this.esc(m.desc || "")}</p>
							</div>`
							)
							.join("")}</div>
					</div>`;
			}

			const services = document.getElementById("restaurant-services-section");
			if (services) {
				const srvs = cfg.services || DEFAULT_CATALOG.services;
				services.innerHTML = `
					<div class="restaurant-wrap">
						<div class="restaurant-section-title">
							<span class="restaurant-eyebrow">Why Choose Us</span>
							<h2>${this.lang === "ar" ? "لماذا تختارنا؟" : "Why Choose Us?"}</h2>
							<p>${this.lang === "ar" ? "نقدم أفضل تجربة طعام مع خدمة استثنائية" : "We provide the best dining experience with exceptional service"}</p>
						</div>
						<div class="restaurant-grid-4">${srvs
							.map((s) => `<div class="restaurant-card">
								<div style="font-size:32px;margin-bottom:12px;">${s.icon}</div>
								<h3>${this.esc(this.lang === "ar" ? s.ar : s.en)}</h3>
							</div>`
							)
							.join("")}</div>
					</div>`;
			}

			const stats = document.getElementById("restaurant-stats");
			if (stats && cfg.stats) {
				const s = cfg.stats;
				stats.innerHTML = `
					<div class="restaurant-wrap restaurant-stats-grid">
						<div><div class="restaurant-stat-num">${s.dishes || 0}</div><div class="restaurant-stat-label">${this.t("dishes")}</div></div>
						<div><div class="restaurant-stat-num">${s.customers || 0}</div><div class="restaurant-stat-label">${this.t("customers")}</div></div>
						<div><div class="restaurant-stat-num">${s.locations || 0}</div><div class="restaurant-stat-label">${this.t("locations")}</div></div>
						<div><div class="restaurant-stat-num">${s.years || 0}</div><div class="restaurant-stat-label">${this.t("years")}</div></div>
					</div>`;
			}

			const cta = document.getElementById("restaurant-cta-band");
			if (cta) {
				cta.innerHTML = `
					<div class="restaurant-wrap">
						<h2>${this.lang === "ar" ? "جاهز لتجربة طعام استثنائية؟" : "Ready for an exceptional dining experience?"}</h2>
						<p>${this.lang === "ar" ? "انضم إلى آلاف العملاء الراضين عن تجربتنا" : "Join thousands of satisfied customers with our experience"}</p>
						<div class="restaurant-hero-cta">
							<a class="restaurant-btn restaurant-btn-accent" href="/app/restaurant-workcenter">${this.lang === "ar" ? "اطلب الآن" : "Order Now"}</a>
							<a class="restaurant-btn restaurant-btn-ghost-light" href="/restaurant#restaurant-services-section">${this.t("learn_more")}</a>
						</div>
					</div>`;
			}
		},
	};
})();
