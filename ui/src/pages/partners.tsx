import { BASE_URL } from "@/utils/utils";
import React from "react";

const Partners = () => {
  return (
    <div className="container">
      <div className="container-inner">
        <div className="partners">
          <h1>Automated data harvest and search utility</h1>
          <p className="mb-3">
            All articles published Open Access through the SCOAP3 initiative,
            with complete metadata and several download formats are publicly
            available on the SCOAP3 repository, in addition to the platforms of
            participating publishers.
          </p>

          <p className="mb-3">
            The SCOAP3 API offers a service to SCOAP3 partners to search and
            download articles and the corresponding metadata. A full
            documentation of the API is available{" "}
            <a
              href="https://github.com/SCOAP3/scoap3-next/wiki/For-partners"
              target="_blank"
              rel="noopener noreferrer"
            >
              here
            </a>
            .
          </p>

          <p className="mb-3">
            The use of the API requires a token which will be provided upon
            registration.
          </p>

          <div className="partners-panels">
            <div className="panel panel-default">
              <div className="panel-body">
                <h3>Create new account</h3>
                <p>
                  To start using SCOAP3 tools (API, etc.) you need first to
                  register.
                </p>
                <a
                  // FIXME add correct url for
                  href={`${BASE_URL}/admin/register`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Register for tools
                </a>
              </div>
            </div>

            <div className="panel panel-default">
              <div className="panel-body">
                <h3>Already registered?</h3>
                <a
                  href={`${BASE_URL}/admin/login`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Login
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Partners;
