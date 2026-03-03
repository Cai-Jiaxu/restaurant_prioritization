import Footer from '@/components/shared/Footer';
import Header from '@/components/shared/Header';

export default function FAQ() {
  return (
    <div className="flex flex-col w-full min-h-screen items-center justify-between fancy-overlay">
      <Header />

      <div className="w-full flex flex-col items-center my-12">
        <section className="w-full p-6 container-narrow">
          <h1 className="text-4xl font-semibold leading-tight md:leading-tight max-w-xs sm:max-w-none md:text-6xl fancy-heading">
            Frequently Asked Questions
          </h1>

          <p className="mt-6 md:text-xl">
            Welcome to the Mevolut FAQ. Here you'll find answers to the most
            common questions about managing your money with us.
          </p>

          <p className="mt-6 md:text-xl">
            <strong>How do I get started with Mevolut?</strong> Signing up is
            easy and free! Simply create an account to start tracking your
            expenses, sending money, and growing your savings securely.
          </p>

          <p className="mt-6 md:text-xl">
            <strong>Is my financial information safe?</strong> Absolutely. We
            prioritize your security with advanced encryption and security
            protocols to keep your data safe.
          </p>

          <p className="mt-6 md:text-xl">
            <strong>Can I use Mevolut on any device?</strong> Yes, our platform
            is fully responsive and accessible from any device with internet
            access.
          </p>

          <p className="mt-6 md:text-xl">
            <strong>
              What features are available to help me manage my money?
            </strong>{' '}
            You can track expenses, send and receive money, set savings goals,
            and view detailed reports to better understand your finances.
          </p>

          <p className="mt-6 md:text-xl">
            <strong>How do I contact support?</strong> For assistance, reach out
            through our support channels inside the app or via email. We're here
            to help!
          </p>
        </section>
      </div>

      <Footer />
    </div>
  );
}
