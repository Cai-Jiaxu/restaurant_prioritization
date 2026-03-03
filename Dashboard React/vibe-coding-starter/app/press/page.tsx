import Footer from '@/components/shared/Footer';
import Header from '@/components/shared/Header';

export default function Press() {
  return (
    <div className="flex flex-col w-full min-h-screen items-center justify-between fancy-overlay">
      <Header />

      <div className="w-full flex flex-col items-center my-12">
        <section className="w-full p-6 container-narrow">
          <h1 className="text-4xl font-semibold leading-tight md:leading-tight max-w-xs sm:max-w-none md:text-6xl fancy-heading">
            Mevolut in the News
          </h1>

          <p className="mt-6 md:text-xl">
            At Mevolut, we're redefining the way you manage your finances. Our
            innovative platform simplifies expense tracking, enables seamless
            money transfers, and helps you grow your savings—all in one secure
            and user-friendly app. Discover how we're making financial
            management accessible for everyone.
          </p>

          <p className="mt-6 md:text-xl">
            Our commitment is to empower users with safe, simple, and efficient
            tools to take control of their financial journey. As we continue to
            grow, we're proud to be recognized for our innovative approach and
            dedication to customer success.
          </p>
        </section>
      </div>

      <Footer />
    </div>
  );
}
